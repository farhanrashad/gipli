# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

TICKET_PRIORITY = [
    ('0', 'Low priority'),
    ('1', 'Medium priority'),
    ('2', 'High priority'),
    ('3', 'Urgent'),
]

class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_sla = fields.Boolean(related='project_id.is_sla')
    is_ticket = fields.Boolean('Ticket', default=False,)

    
    ticket_priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='0', tracking=True)
    
    # SLA fields
    sla_date_deadline = fields.Datetime("SLA Deadline", compute='_compute_all_sla_deadline', compute_sudo=True, store=True)
    sla_hours_deadline = fields.Float("Hours to SLA Deadline", compute='_compute_all_sla_deadline', compute_sudo=True, store=True)
    prj_task_sla_line = fields.One2many('project.task.sla.line', 'task_id', string="SLA Line")
    
    
    domain_user_ids = fields.Many2many('res.users', compute='_compute_domain_from_project')
    prj_ticket_type_id = fields.Many2one('project.ticket.type', string="Type", tracking=True)

    partner_phone = fields.Char(string='Customer Phone', compute='_compute_phone_from_partner', inverse="_compute_inverse_phone_from_partner", store=True, readonly=False)
    partner_email = fields.Char(string='Customer Email', compute='_compute_email_from_partner', inverse="_inverse_partner_email", store=True, readonly=False)

    is_update_partner_email = fields.Boolean('Partner Email will Update', compute='_compute_is_update_partner_email')
    is_update_partner_phone = fields.Boolean('Partner Phone will Update', compute='_compute_is_update_partner_phone')

    ticket_no = fields.Char(
        string="Ticket No",
        copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('/'))

    closed_by = fields.Selection([
        ('customer', 'Closed by Customer'), 
        ('user', 'Closed by User')],
        string='Closed Type',
    )
    #Customer Rating
    allow_customer_rating = fields.Boolean(related='project_id.allow_customer_rating')
    rating = fields.Selection(
        [('1', 'Poor'), ('2', 'Fair'), ('3', 'Average'), ('4', 'Good'), ('5', 'Excellent')],
        string='Rating'
    )
    rating_comment = fields.Text(string='Rating Comment')
    rating_score = fields.Integer(string='Rating Scroe', compute='_compute_customer_rating')

    # Re-open Tickets
    prj_ticket_reopen_ids = fields.One2many('project.ticket.reopen', 'ticket_id', string="Re-Open Reasons")
    count_reopen = fields.Integer(string='Reopen Number', compute='_compute_reopen_count')
    allowed_reopen = fields.Boolean(string='Allow Reopen', compute='_compute_allow_reopen')

    
    # Computed Methods
    def _compute_allow_reopen(self):
        for record in self:
            record.allowed_reopen = True
            
    def _compute_reopen_count(self):
        for record in self:
            record.count_reopen = len(record.prj_ticket_reopen_ids)
            
    @api.depends('closed_by')
    def _update_stage_on_closed_by(self):
        stage_id = self.env['project.task.type']
        for record in self:
            stage_id = self.env['project.task.type'].search([
                ('fold','=',True),
                ('project_ids','=',self.project_id.id)
            ],limit=1)
            record.write({
                'stage_id': stage_id.id,
            })
    def _compute_customer_rating(self):
        for record in self:
            record.rating_score = int(record.rating)
        
    @api.model
    def _compute_task_priority(self):
        if self._context.get('default_is_ticket') or self.project_id.is_helpdesk_team:
            return TICKET_PRIORITY
        else:
            return PROJECT_PRIORITY

    
    #@api.depends('sla_status_ids.deadline', 'sla_status_ids.reached_datetime')
    def _compute_all_sla_deadline(self):
        for record in self:
            record.sla_date_deadline = False
            record.sla_hours_deadline = False

    @api.depends('project_id')
    def _compute_domain_from_project(self):
        user_ids = self.env.ref('de_helpdesk.group_project_helpdesk_user').users.ids
        for ticket in self:
            ticket_user_ids = []
            ticket_sudo = ticket.sudo()
            if ticket_sudo.project_id and ticket_sudo.project_id.privacy_visibility == 'invited_internal':
                ticket_user_ids = ticket_sudo.project_id.message_partner_ids.user_ids.ids
            ticket.domain_user_ids = [Command.set(user_ids + ticket_user_ids)]

    @api.depends('partner_id.phone')
    def _compute_phone_from_partner(self):
        for ticket in self:
            if ticket.partner_id:
                ticket.partner_phone = ticket.partner_id.phone

    def _compute_inverse_phone_from_partner(self):
        for ticket in self:
            if ticket._get_partner_phone_update() or not ticket.partner_id.phone:
                ticket.partner_id.phone = ticket.partner_phone

    @api.depends('partner_id.email')
    def _compute_email_from_partner(self):
        for ticket in self:
            if ticket.partner_id:
                ticket.partner_email = ticket.partner_id.email

    def _compute_inverse_email_from_partner(self):
        for ticket in self:
            if ticket._get_partner_email_update():
                ticket.partner_id.email = ticket.partner_email
                
    @api.depends('partner_email', 'partner_id')
    def _compute_is_update_partner_email(self):
        for ticket in self:
            ticket.is_update_partner_email = ticket._get_partner_email_update()

    @api.depends('partner_phone', 'partner_id')
    def _compute_is_update_partner_phone(self):
        for ticket in self:
            ticket.is_update_partner_phone = ticket._get_partner_phone_update()

    def _get_partner_email_update(self):
        self.ensure_one()
        if self.partner_id.email and self.partner_email != self.partner_id.email:
            ticket_email_normalized = tools.email_normalize(self.partner_email) or self.partner_email or False
            partner_email_normalized = tools.email_normalize(self.partner_id.email) or self.partner_id.email or False
            return ticket_email_normalized != partner_email_normalized
        return False

    def _get_partner_phone_update(self):
        self.ensure_one()
        if self.partner_id.phone and self.partner_phone != self.partner_id.phone:
            ticket_phone_formatted = self.partner_phone or False
            partner_phone_formatted = self.partner_id.phone or False
            return ticket_phone_formatted != partner_phone_formatted
        return False


    # -----------------------------------------------------------------------------
    # ------------------------------ CRUD Operations ------------------------------ 
    # -----------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        tasks = super(ProjectTask, self).create(vals_list)
        created_sla_lines = self._prepare_sla_lines(tasks)
        for task in tasks:
            if task.is_ticket or (task.project_id and task.project_id.is_helpdesk_team):
                task.ticket_no = self.env['ir.sequence'].next_by_code('project.task.ticket.no')
        return tasks
        
    def _prepare_sla_lines(self, tasks):
        sla_lines = self.env['project.task.sla.line']
        current_date = datetime.now()
        
        for task in tasks:
            if task.is_sla and task.project_id.is_helpdesk_team:
                sla_ids = self.env['project.sla'].search([('project_id','=',task.project_id.id)])
                for sla in sla_ids:
                    sla_line = self.env['project.task.sla.line'].create({
                        'task_id': task.id,
                        'prj_sla_id': sla.id,
                        'date_deadline': current_date + timedelta(days=sla.time)  # Assuming time is in days
                    })
                    sla_lines |= sla_line
        return sla_lines

    @api.model
    def _check_stage_access(self, stage_id, ticket_approval_type, group_ids, user_ids):
        if not stage_id:
            return True  # Allow empty stages
    
        if ticket_approval_type == 'group' and group_ids:
            # Check if the current user belongs to any of the required groups for the stage
            allowed_groups = group_ids.ids
            user_groups = self.env.user.groups_id.ids
            return bool(set(allowed_groups) & set(user_groups))
    
        if ticket_approval_type == 'user' and user_ids:
            # Check if the current user is one of the specified users for the stage
            return self.env.user.id in user_ids.ids
    
        return True  # Allow if no specific group or user is defined
    
    def write(self, vals):
        if 'stage_id' in vals:
            new_stage_id = vals['stage_id'] if vals['stage_id'] else self.stage_id.id
            project = self.project_id
            if project.is_helpdesk_team:
                ticket_approvals = self.env['project.task.type.approvals'].search([
                    ('ticket_stage_id', '=', new_stage_id),
                    ('project_id', '=', self.project_id.id),
                ])
        
                if ticket_approvals:
                    approval = ticket_approvals[0]  # Assume there's only one approval record
                    if not self._check_stage_access(
                        new_stage_id,
                        approval.ticket_approval_type,
                        approval.group_ids,
                        approval.user_ids
                    ):
                        raise ValidationError(_("You don't have access to change the stage."))
        
        return super(ProjectTask, self).write(vals)


    # ------------------------------------------------------------------------
    # ------------------------------ actions ---------------------------------
    # ------------------------------------------------------------------------
    def _get_ticket_reopen_digest(self, reason, template='de_helpdesk.project_ticket_reopen_digest', lang=None):
        self.ensure_one()
        values = {
                  'reason': reason,
                 }
        return self.env['ir.qweb'].with_context(lang=lang)._render(template, values)

    def _get_ticket_merge_digest(self, ticket, template='de_helpdesk.merge_tickets_digest', lang=None):
        self.ensure_one()
        values = {
            'record_url': ticket._get_html_link(),
            'assignees': ','.join(user.name for user in ticket.user_ids),
            'project': ticket.project_id.name
        }
        return self.env['ir.qweb'].with_context(lang=lang)._render(template, values)

    def _prepare_new_merge_ticket_values(self, name, description):
        #user_id = [(4, self.user_id.id)] if self.user_id else False
        vals = {
            'name': name,
            'project_id': self.project_id.id,
            'user_ids': self.user_ids,
            'description': description,
            'is_ticket': True,
        }
       
        return vals
        
    def open_reopen_ticket_reaons(self):
        action = self.env.ref('de_helpdesk.action_ticket_reopen_reason').read()[0]
        action.update({
            'name': 'Reopen Reasons',
            'view_mode': 'tree',
            'res_model': 'project.ticket.reopen',
            'type': 'ir.actions.act_window',
            'domain': [('ticket_id','=',self.id)],
            'context': {
                'create': False,
                'edit': False,
            },
            
        })
        return action

    def _prepare_ticket_reopen_reason_values(self, ticket, reason):
        #if self.env.user
        reopen_by = 'user'
        return {
            'ticket_id': ticket.id,
            'reopen_by': reopen_by,
            'name': reason,
            'date_reopen': fields.Datetime.now(),
        }
    def _prepare_ticket_reopen(self, stage_id):
        return {
            'closed_by': False,
            'stage_id': stage_id.id,
        }

    def _action_merge_tickets(self):
        active_ids = self.env.context.get('active_ids')
        ticket_ids = self.env['project.task'].search([('id','in',active_ids)])
        partner_ids = ticket_ids.mapped('partner_id')
        if len(partner_ids) != 1:
            raise UserError('Merging tickets for multiple customers is not allowed.')
        if any(ticket.stage_id.fold for ticket in ticket_ids):
            raise UserError(_("One or more tickets are already closed and cannot be merged."))
        if len(active_ids) == 1:
            raise UserError(_("Please select two or more tickets to merge."))
        if any(not ticket.project_id.is_helpdesk_team for ticket in ticket_ids):
            raise UserError(_("At least one of the selected teams or projects is not eligible for merging tickets."))
        return {
            'name': 'Merge Tickets',
            'view_mode': 'form',
            'res_model': 'project.ticket.merge.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
    def action_reopen_tickets(self):
        active_ids = self.env.context.get('active_ids')
        ticket_ids = self.env['project.task'].search([('id','in',active_ids)]) 
        project_ids = ticket_ids.mapped('project_id')
        #raise UserError(ticket_ids)
        if len(project_ids) > 1:
            raise UserError('It is not permissible to reopen tickets concurrently across different support groups.')
        if any(not ticket.project_id.is_helpdesk_team for ticket in ticket_ids):
            raise UserError(_("At least one of the selected teams or projects is not eligible for merging tickets."))
        if any(not ticket.stage_id.fold for ticket in ticket_ids):
            raise UserError(_("One or more tickets are already open."))
        return {
            'name': 'Reopen Ticket',
            'view_mode': 'form',
            'res_model': 'project.ticket.reopen.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
