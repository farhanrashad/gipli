# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, tools, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.addons.web.controllers.utils import clean_action

from odoo.osv import expression


import pytz
import logging


TICKET_PRIORITY = [
    ('0', 'Low priority'),
    ('1', 'Medium priority'),
    ('2', 'High priority'),
    ('3', 'Urgent'),
]
_logger = logging.getLogger(__name__)

class ProjectTicket(models.Model):
    _inherit = 'project.task'

    is_sla = fields.Boolean(related='project_id.is_sla')
    is_ticket = fields.Boolean('Ticket', default=False,)

    
    ticket_priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='0', tracking=True)
    
    # SLA fields
    sla_date_deadline = fields.Datetime("SLA Deadline", compute='_compute_all_sla_deadline', compute_sudo=True, store=True)
    sla_hours_deadline = fields.Float("Hours to SLA Deadline", compute='_compute_all_sla_deadline', compute_sudo=True, store=True)
    ticket_sla_ids = fields.One2many('project.ticket.sla.line', 'ticket_id', readonly=True, string="SLA Line")
    is_sla_fail = fields.Boolean("Failed SLA Policy", compute='_compute_ticket_sla_fail', search='_search_failed_sla')
    is_sla_success = fields.Boolean("Success SLA Policy", compute='_compute_ticket_sla_success', search='_search_success_sla')
    #date_sla_deadline = fields.Datetime('SLA Deadline', help='The date on which the SLA should close')
    
    
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
    date_closed = fields.Datetime('Close on', 
                                   help='The date on which the ticket closed')
    hours_close = fields.Integer("Time to close (hours)", compute='_get_closing_hours', store=True)
    #Customer Rating
    allow_customer_rating = fields.Boolean(related='project_id.allow_customer_rating')
    customer_rating = fields.Selection(
        [('1', 'Poor'), ('2', 'Fair'), ('3', 'Average'), ('4', 'Good'), ('5', 'Excellent')],
        string='Rating'
    )
    rating_comment = fields.Text(string='Rating Comment')
    rating_score = fields.Integer(string='Rating Scroe', 
                                  store=True,
                                  compute='_compute_customer_rating'
                                 )

    # Re-open Tickets
    prj_ticket_reopen_ids = fields.One2many('project.ticket.reopen', 'ticket_id', string="Re-Open Reasons")
    count_reopen = fields.Integer(string='Reopen Number', compute='_compute_reopen_count')
    allowed_reopen = fields.Boolean(string='Allow Reopen', compute='_compute_allow_reopen')

    
    # Computed Methods
    @api.depends('sla_status_ids.deadline', 'sla_status_ids.reached_datetime')
    def _compute_sla_reached(self):
        sla_status_read_group = self.env['helpdesk.sla.status']._read_group(
            [('exceeded_hours', '<', 0), ('ticket_id', 'in', self.ids)],
            ['ticket_id'],
        )
        sla_status_ids_per_ticket = {ticket.id for [ticket] in sla_status_read_group}
        for ticket in self:
            ticket.sla_reached = ticket.id in sla_status_ids_per_ticket
            
    @api.depends('sla_status_ids.deadline', 'sla_status_ids.reached_datetime')
    def _compute_sla_reached_late(self):
        """ Required to do it in SQL since we need to compare 2 columns value """
        mapping = {}
        if self.ids:
            self.env.cr.execute("""
                SELECT ticket_id, COUNT(id) AS reached_late_count
                FROM helpdesk_sla_status
                WHERE ticket_id IN %s AND (deadline < reached_datetime OR (deadline < %s AND reached_datetime IS NULL))
                GROUP BY ticket_id
            """, (tuple(self.ids), fields.Datetime.now()))
            mapping = dict(self.env.cr.fetchall())

        for ticket in self:
            ticket.sla_reached_late = mapping.get(ticket.id, 0) > 0
            
    @api.depends('sla_date_deadline')
    def _compute_ticket_sla_fail(self):
        current_time = fields.Datetime.now()
        for record in self:
            if record.sla_date_deadline:
                record.is_sla_fail = (record.sla_date_deadline < current_time)
            

    @api.model
    def _search_failed_sla(self, operator, value):
        datetime_now = fields.Datetime.now()
        domain = []
        if (value and operator in expression.NEGATIVE_TERM_OPERATORS) or (not value and operator not in expression.NEGATIVE_TERM_OPERATORS):
            domain = ['|', ('sla_date_deadline', '=', False), ('sla_date_deadline', '>=', datetime_now)]
        else:
            domain = [('sla_date_deadline', '<', datetime_now)]
        return domain

    
    @api.depends('sla_date_deadline')
    def _compute_ticket_sla_success(self):
        current_time = fields.Datetime.now()
        for record in self:
            record.is_sla_success = (record.sla_date_deadline and record.sla_date_deadline > current_time)


    @api.model
    def _search_success_sla(self, operator, value):
        datetime_now = fields.Datetime.now()
        domain = []
        if (value and operator in expression.NEGATIVE_TERM_OPERATORS) or (not value and operator not in expression.NEGATIVE_TERM_OPERATORS):
            domain = [('ticket_sla_ids.date_reached', '>', datetime_now), '|', ('sla_date_deadline', '!=', False), ('sla_date_deadline', '<', datetime_now)]
        else:
            domain = [('ticket_sla_ids.date_reached', '<', datetime_now), '|', ('sla_date_deadline', '=', False), ('sla_date_deadline', '>=', datetime_now)]
        return domain
        
    @api.depends('create_date', 'date_closed')
    def _get_closing_hours(self):
        for record in self:
            create_date = fields.Datetime.from_string(record.create_date)
            if create_date and record.date_closed and record.team:
                duration_data = record.team.calendar.get_work_duration_data(
                    create_date,
                    fields.Datetime.from_string(record.date_closed),
                    compute_leaves=True
                )
                record.hours_close = duration_data['hours']
            else:
                record.hours_close = False
            
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

    @api.depends('customer_rating')
    def _compute_customer_rating(self):
        for record in self:
            record.rating_score = int(record.customer_rating)
        
    @api.model
    def _compute_ticket_priority(self):
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
        tickets = super(ProjectTicket, self).create(vals_list)
        created_sla_lines = self._prepare_sla_lines(tickets)
        for ticket in tickets:
            if ticket.is_ticket or (ticket.project_id and ticket.project_id.is_helpdesk_team):
                ticket.ticket_no = self.env['ir.sequence'].next_by_code('project.task.ticket.no')

            # Check if automatic assignment is enabled and assign_method is valid
            if ticket.project_id.auto_assignment and ticket.project_id.assign_method in ['balanced', 'randomly']:
                # Assign users to the ticket based on the assign_method
                self._assign_user(ticket)

             # Check if automatic assignment is enabled and assign_method is valid
            if ticket.project_id.auto_assignment and ticket.project_id.assign_method in ['equal', 'random']:
                # Assign users to the ticket based on the assign_method
                self._assign_user(ticket)
            
        return tickets


    def _calculate_deadline_date(self, sla_hours, create_date):
        _logger.info("Calculating deadline date...")
        _logger.info(f"SLA Hours: {sla_hours}, Create Date: {create_date}")

        # Convert create_date to datetime object
        from_datetime = fields.Datetime.from_string(create_date)

        # Calculate to_datetime based on SLA hours
        to_datetime = from_datetime + timedelta(hours=sla_hours)

        _logger.info(f"From Datetime: {from_datetime}, To Datetime: {to_datetime}")

        # Initialize work_duration_data
        work_duration_data = {}

        try:
            # Get work duration data with compute_leaves=True and domain=None
            work_duration_data = self.project_id.resource_calendar_id.get_work_duration_data(
                from_datetime,
                to_datetime,
                compute_leaves=True,
                domain=None
            )
            _logger.info(f"Work Duration Data: {work_duration_data}")
        except Exception as e:
            _logger.error(f"Error while getting work duration data: {e}")

        # Calculate deadline date based on work duration data if available
        deadline_date = to_datetime + timedelta(
            days=work_duration_data.get('days', 0),
            hours=work_duration_data.get('hours', 0)
        )

        _logger.info(f"Deadline Date: {deadline_date}")

        return deadline_date
        
    def _prepare_sla_lines(self, tickets):
        sla_lines = self.env['project.ticket.sla.line']
        current_date = datetime.now()

        for ticket in tickets:
            if ticket.is_sla and ticket.project_id.is_helpdesk_team:
                ticket.ticket_sla_ids.unlink()
                sla_ids = self.env['project.sla'].search([('project_id','=',ticket.project_id.id)])

                for sla in sla_ids:
                    deadline_date = self._calculate_deadline_date(
                        sla.time,  # SLA time in hours
                        ticket.create_date  # Ticket's create date
                    )
                    sla_line = self.env['project.ticket.sla.line'].create({
                        'ticket_id': ticket.id,
                        'prj_sla_id': sla.id,
                        'date_deadline': deadline_date
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
                ticket_approvals = self.env['project.ticket.stage.approvals'].search([
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

            if project.is_sla:
                #raise UserError(new_stage_id)
                tickets_to_update = self.filtered(lambda t: t.is_sla and t.project_id.is_helpdesk_team)
                for ticket in tickets_to_update:
                    if ticket.ticket_sla_ids:
                        ticket.ticket_sla_ids._update_sla_status(new_stage_id)
                
                # Update SLA line statuses based on stage and deadline conditions
                #sla_lines_to_update = self.env['project.ticket.sla.line'].search([('ticket_id', '=', self.id)])
                #sla_lines_to_update._update_sla_status()


        # Call super write to update the ticket
        res = super(ProjectTicket, self).write(vals)

        # Check if project_id changed
        if 'project_id' in vals:
            new_project_id = vals['project_id'] if vals['project_id'] else self.project_id.id
            tickets_to_update = self.filtered(lambda t: t.is_sla and t.project_id.is_helpdesk_team)
            # Call _prepare_sla_lines for tickets to be updated
            self._prepare_sla_lines(tickets_to_update)
        
        return res


    # -----------------------------------------------------------------------
    # ---------------------------- Business Logics --------------------------
    # -----------------------------------------------------------------------
    # Auto Assignment of Tickets
    def _assign_user(self, ticket):
        active_users = ticket.project_id.team_member_ids.filtered(lambda user: user.active)
        if active_users:
            if ticket.project_id.assign_method == 'equal':
                self._assign_equal(ticket, active_users)
            elif ticket.project_id.assign_method == 'random':
                self._assign_random(ticket, active_users)
    
    def _assign_equal(self, ticket, active_users):
        # Calculate the user index based on the total number of tickets assigned to users
        user_index = ticket.id % len(active_users)
        ticket.user_ids = [(4, active_users[user_index].id)]
    
    def _assign_random(self, ticket, active_users):
        # Assign users randomly using round-robin method
        user_index = len(ticket.project_id.task_ids) % len(active_users)
        ticket.user_ids = [(4, active_users[user_index].id)]

        
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

    def action_ticket_all(self, action_ref, title, search_view_ref,context=None):
        #raise UserError(action_ref)
        if action_ref == 'de_helpdesk.action_set_target':
            return {
                'name': 'Set Target',
                'view_mode': 'form',
                'res_model': 'project.helpdesk.user.target.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        if context is None:
            context = {} 
        #raise UserError(context)
        action = self.env["ir.actions.actions"]._for_xml_id(action_ref)
        action = clean_action(action, self.env)
        if title:
            action['display_name'] = title
        if search_view_ref:
            action['search_view_id'] = self.env.ref(search_view_ref).read()[0]
        if 'views' not in action:
            action['views'] = [(False, view) for view in action['view_mode'].split(",")]
        action['context'] = {
            **context, 
            'create': False, 
            'edit': False, 
            'delete': False,
        }
        return action
