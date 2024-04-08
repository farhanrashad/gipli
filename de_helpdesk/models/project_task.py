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
    is_ticket = fields.Boolean('Ticket', default=False, store=True, 
                              compute='_compute_is_ticket'
                              )

    
    ticket_priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='0', tracking=True)
    
    # SLA fields
    ticket_sla_ids = fields.One2many('project.ticket.sla.line', 'ticket_id', readonly=True, string="SLA Line")
    sla_date_deadline = fields.Datetime("SLA Deadline", compute='_compute_all_sla_ticket_deadline', compute_sudo=True, store=True)
    sla_hours_deadline = fields.Float("Hours to SLA Deadline", compute='_compute_all_sla_ticket_deadline', compute_sudo=True, store=True)
    
    is_sla_fail = fields.Boolean("Failed SLA Policy", compute='_compute_ticket_sla_fail', search='_search_failed_sla')
    is_sla_success = fields.Boolean("Success SLA Policy", compute='_compute_ticket_sla_success', search='_search_success_sla')
    #date_sla_deadline = fields.Datetime('SLA Deadline', help='The date on which the SLA should close')
    
    
    domain_user_ids = fields.Many2many('res.users', compute='_compute_domain_from_project')
    prj_ticket_type_id = fields.Many2one('project.ticket.type', 
                                         string="Type", 
                                         tracking=True,
                                         domain="['|',('project_id','=',False),('project_id','=',project_id)]"
                                        )

    partner_phone = fields.Char(string='Customer Phone', compute='_compute_phone_from_partner', inverse="_compute_inverse_phone_from_partner", store=True, readonly=False)
    partner_email = fields.Char(string='Customer Email', compute='_compute_email_from_partner', inverse="_compute_inverse_email_from_partner", store=True, readonly=False)

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
        string='Closed Type', readonly=True,
    )
    date_closed = fields.Datetime('Close on', readonly=True,
                                   help='The date on which the ticket closed')
    hours_close = fields.Integer("Time to close (hours)", compute='_get_closing_hours', store=True, readonly=True)
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
    allow_reopen = fields.Boolean(compute='_compute_allow_reopen')
    reopen_reason = fields.Text('Reason for Reopen Ticket')

    allow_history = fields.Boolean(compute='_compute_allow_history')
    ticket_log_ids = fields.One2many('project.ticket.log', 'ticket_id', string="Ticket History")
    count_ticket_history = fields.Integer(string='Ticket Log', compute='_compute_ticket_history_count')

    # Portal Options
    allow_portal_user_close_ticket = fields.Boolean(compute='_compute_portal_close_ticket')
    allow_portal_user_reopen_ticket = fields.Boolean(compute='_compute_portal_reopen_ticket')
    
    # Computed Methods
    @api.depends('project_id.is_helpdesk_team')
    def _compute_is_ticket(self):
        for record in self:
            if record.project_id.is_helpdesk_team:
                record.is_ticket = True

            
    @api.depends('sla_date_deadline')
    def _compute_ticket_sla_fail(self):
        current_time = fields.Datetime.now()
        for record in self:
            if record.sla_date_deadline:
                record.is_sla_fail = (record.sla_date_deadline < current_time)
            else:
                record.is_sla_fail = False
            

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
            if create_date and record.date_closed and record.project_id.is_helpdesk_team:
                duration_data = record.project_id.resource_calendar_id.get_work_duration_data(
                    create_date,
                    fields.Datetime.from_string(record.date_closed),
                    compute_leaves=True
                )
                record.hours_close = duration_data['hours']
            else:
                record.hours_close = False

    def _compute_portal_close_ticket(self):
        for record in self:
            if record.project_id.allow_portal_user_close_ticket and not record.stage_id.fold:
                record.allow_portal_user_close_ticket = True
            else:
                record.allow_portal_user_close_ticket = False

    def _compute_allow_reopen(self):
        for record in self:
            if record.project_id.is_reopen_tickets and record.stage_id.fold:
                record.allow_reopen = True
            else:
                record.allow_reopen = False

    def _compute_allow_history(self):
        for record in self:
            if record.project_id.is_history_tickets:
                record.allow_history = True
            else:
                record.allow_history = False
    
    def _compute_portal_reopen_ticket(self):
        for record in self:
            if record.project_id.allow_portal_user_reopen_ticket and record.stage_id.fold:
                record.allow_portal_user_reopen_ticket = True
            else:
                record.allow_portal_user_reopen_ticket = False
            
    def _compute_reopen_count(self):
        for record in self:
            record.count_reopen = len(record.prj_ticket_reopen_ids)

    def _compute_ticket_history_count(self):
        for record in self:
            record.count_ticket_history = len(record.ticket_log_ids)
            
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

    
    @api.depends('ticket_sla_ids.date_deadline', 'ticket_sla_ids.date_reached')
    def _compute_all_sla_ticket_deadline(self):
        """
        Compute the SLA deadline and hours remaining based on current status for each ticket.
        """
        current_time = fields.Datetime.now()
    
        for ticket in self:
            min_deadline = False
    
            # Find the minimum deadline among all SLA statuses for the ticket
            for status in ticket.ticket_sla_ids:
                if status.date_reached or not status.date_deadline:
                    continue
    
                if not min_deadline or status.date_deadline < min_deadline:
                    min_deadline = status.date_deadline
    
            # Update the ticket's SLA fields based on the minimum deadline
            ticket.update({
                'sla_date_deadline': min_deadline,
                'sla_hours_deadline': (
                    ticket.project_id.resource_calendar_id.get_work_duration_data(
                        current_time, min_deadline, compute_leaves=True
                    )['hours']
                    if min_deadline
                    else 0.0
                ),
            })

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
        created_sla_lines = self._compute_sla_lines(tickets)
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
            #new_stage_id = vals['stage_id'] if vals['stage_id'] else self.stage_id.id
            new_stage_id = self.env['project.task.type'].browse(vals['stage_id'] if vals['stage_id'] else self.stage_id.id)
            project = self.project_id

            # Ticket Approvals
            if project.is_helpdesk_team:
                ticket_approvals = self.env['project.ticket.stage.approvals'].search([
                    ('ticket_stage_id', '=', new_stage_id.id),
                    ('project_id', '=', self.project_id.id),
                ])
        
                if ticket_approvals:
                    approval = ticket_approvals[0]  # Assume there's only one approval record
                    if not self._check_stage_access(
                        new_stage_id.id,
                        approval.ticket_approval_type,
                        approval.group_ids,
                        approval.user_ids
                    ):
                        raise ValidationError(_("You don't have access to change the stage."))

            # Reopen Ticket ----------
            #if 'reopen_reason' in vals:
            #    self._create_reopen_ticket_reason(self, vals.get('reopen_reason'))
            #else: #if not vals.get('reopen_reason'):
            ticket = self.filtered(lambda t: t.is_ticket and t.project_id.is_reopen_tickets)
            if ticket:
                ticket._reopen_ticket(ticket, new_stage_id=new_stage_id, reason=vals.get('reopen_reason'))
            #ticket._create_reopen_ticket_reason(ticket, reason=False)
            
            # Maintain Ticket Log 
            tickets = self.filtered(lambda t: t.is_ticket and t.project_id.is_history_tickets)
            if tickets:
                for ticket in tickets:
                    ticket._create_ticket_log(ticket, ticket.stage_id, new_stage_id)
            
            # Update SLA
            if project.is_sla:
                #raise UserError(new_stage_id.id)
                tickets_to_update = self.filtered(lambda t: t.is_sla and t.project_id.is_helpdesk_team)
                for ticket in tickets_to_update:
                    if ticket.ticket_sla_ids:
                        #ticket.ticket_sla_ids._update_sla_status(new_stage_id.id)
                        ticket._update_sla_lines(ticket, vals.get('stage_id'))
            self._update_ticket(vals.get('stage_id'))
                
        
            
        #ticket_ids_to_sla = self.filtered(lambda t: t.is_sla and t.project_id.is_helpdesk_team)
        #raise UserError(ticket_ids_to_sla.ticket_sla_ids)
        #if not len(ticket_ids_to_sla.ticket_sla_ids):
        #    created_sla_lines = self._compute_sla_lines(ticket_ids_to_sla)
        #raise UserError(ticket_ids_to_sla)

        # Call super write to update the ticket
        res = super(ProjectTicket, self).write(vals)

        # Recompute SLA Lines
        if 'partner_id' in vals or 'prj_ticket_type_id' in vals or 'ticket_priority' in vals or 'tag_ids' in vals:
            #new_project_id = vals['project_id'] if vals['project_id'] else self.project_id.id
            tickets_to_update = self.filtered(lambda t: t.is_sla and t.project_id.is_helpdesk_team)
            # Call _compute_sla_lines for tickets to be updated
            self._compute_sla_lines(tickets_to_update)
        
        return res


    # -----------------------------------------------------------------------
    # ---------------------------- Business Logics --------------------------
    # -----------------------------------------------------------------------
    # Update Ticket close fields ----------------
    def _update_ticket(self, stage_id):
        ticket_stage_id = self.env['project.task.type'].browse(stage_id)
        if ticket_stage_id.fold:
            if self.env.user.has_group('base.group_portal'):
                self.closed_by = 'customer'
            else:
                self.closed_by = 'user'
            self.date_closed = fields.Datetime.now()
        else:
            self.closed_by = False
            self.date_closed = False
            
    # ------------ Apply SLA ------------
    def _update_sla_lines(self, ticket, stage_id):
        new_stage_id = self.env['project.task.type'].browse(stage_id)
        for sla_line in ticket.ticket_sla_ids:
            if sla_line.prj_sla_id.stage_id.id == new_stage_id.id:
                sla_line.date_reached = fields.Datetime.now()
            elif new_stage_id.sequence < sla_line.prj_sla_id.stage_id.sequence:
                sla_line.date_reached = False
            else:
                if not sla_line.date_reached:
                    sla_line.date_reached = fields.Datetime.now()



    def _find_sla_ids(self, ticket):
        domain = [('project_id', '=', ticket.project_id.id)]
    
        sla_policies = self.env['project.sla'].search([('project_id', '=', ticket.project_id.id)])
        filter_sla_policies = sla_policies

        
    
        #if sla_policies:
        #    prj_ticket_type_ids = sla_policies.mapped('prj_ticket_type_ids')
        #    if ticket.prj_ticket_type_id not in prj_ticket_type_ids:
        #        sla_policies = sla_policies.filtered(lambda p: not p.prj_ticket_type_ids)
        if sla_policies:

            # add domain for ticket type
            prj_ticket_domain = []
            prj_ticket_type_ids = sla_policies.mapped('prj_ticket_type_ids')
            if prj_ticket_type_ids:
                if ticket.prj_ticket_type_id in prj_ticket_type_ids:
                    prj_ticket_domain += ['|',('prj_ticket_type_ids','in',ticket.prj_ticket_type_id.id),('prj_ticket_type_ids','=',False)]
                else:
                    prj_ticket_domain += [('prj_ticket_type_ids','=',False)]

            
            # add domain for partner
            partner_domain = []
            partner_ids = sla_policies.mapped('partner_ids')
            if partner_ids:
                if ticket.partner_id in partner_ids:
                    partner_domain += ['|',('partner_ids','in',ticket.partner_id.id),('partner_ids','=',False)]
                else:
                    partner_domain += [('partner_ids','=',False)]

            # add domain for pririty
            priority_domain = []
            priorities = sla_policies.filtered(lambda x:x.priority != '0').mapped('priority')
            #for sla in sla_policies:
            #    if sla.priority == ticket.ticket_priority:
            #        priority_domain += 
            if priorities:
                if ticket.ticket_priority in priorities:
                    priority_domain += ['|',('priority','=',ticket.ticket_priority),('priority','!=',priorities)]
                else:
                    priority_domain += [('priority','!=',priorities)]
            #priority_domain = [('priority', '=', ticket.ticket_priority)]
            
            # add domain for tag ids
            tags_domain = []
            tag_ids = sla_policies.mapped('tag_ids')
            if tag_ids:
                if any(tag_id in tag_ids.ids for tag_id in ticket.tag_ids.ids):
                    #if tag_ids.ids in ticket.tag_ids.ids:
                    tags_domain += ['|',('tag_ids', 'in', ticket.tag_ids.ids),('tag_ids', '=', False)]
                else:
                    tags_domain += [('tag_ids', '=', False)]

            domain += expression.AND([prj_ticket_domain, partner_domain, tags_domain, priority_domain])
            #partner_ids = sla_policies.mapped('partner_ids')
            #if ticket.prj_ticket_type_id not in prj_ticket_type_ids:
            #    domain += [('prj_ticket_type_ids','in',ticket.prj_tikcet_type_id.id)]

        filter_sla_policies = filter_sla_policies.search(domain)
        #self.message_post(body=f'tags={ticket.tag_ids.ids}')
        #self.message_post(body=f'sla tags={tag_ids.ids}')
        #self.message_post(body=domain)
        return filter_sla_policies



    def _calculate_deadline_date(self, ticket, sla):
        # Convert create_date to datetime object
        from_datetime = fields.Datetime.from_string(ticket.create_date)

        # Calculate to_datetime based on SLA hours
        to_datetime = from_datetime + timedelta(hours=sla.time)

        # Initialize work_duration_data
        work_duration_data = {}

        # Get work duration data with compute_leaves=True and domain=None
        work_duration_data = ticket.project_id.resource_calendar_id.get_work_duration_data(
            from_datetime,
            to_datetime,
            compute_leaves=True,
            domain=None
        )

        # Calculate deadline date based on work duration data if available
        deadline_date = to_datetime + timedelta(
            days=work_duration_data.get('days', 0),
            hours=work_duration_data.get('hours', 0)
        )

        return deadline_date
        
    def _compute_sla_lines(self, tickets):
        sla_lines = self.env['project.ticket.sla.line']
        current_date = datetime.now()
        tickets.ticket_sla_ids.unlink()
        for ticket in tickets:
            if ticket.is_sla and ticket.project_id.is_helpdesk_team:
                #raise UserError(ticket.project_id)
                #ticket.ticket_sla_ids.unlink()
                sla_ids = self.sudo()._find_sla_ids(ticket)
                if sla_ids:
                    for sla in sla_ids:
                        sla_line_vals = self._prpeare_sla_line_values(ticket, sla)
                        sla_line = self.env['project.ticket.sla.line'].create(sla_line_vals)
                        sla_lines |= sla_line
        return sla_lines
        
    def _prpeare_sla_line_values(self, ticket, sla):
        deadline_date = self._calculate_deadline_date(
            ticket,  
            sla
        )
        return {
            'ticket_id': ticket.id,
            'prj_sla_id': sla.id,
            'date_deadline': deadline_date,
        }
    
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


    # Reopen Tickets
    def _reopen_ticket(self, ticket, new_stage_id=False, reason=False):
        min_open_stage = self.env['project.task.type'].search([
            ('project_ids','in',ticket.project_id.id),
            ('active','=',True),
            ('fold','=',False),
        ], order='sequence', limit=1)
        if min_open_stage:
            min_stage_id = min_open_stage[0]

        vals = {}
        if not reason:
            reason = 'Reopen By User'
        
        if not new_stage_id:
            vals['stage_id'] = min_stage_id.id
            
        if (new_stage_id and new_stage_id.id == min_stage_id.id) or not new_stage_id:
            #ticket.sudo().update(vals)
            ticket.sudo()._create_reopen_ticket_reason(ticket,reason)
            lang = ticket.partner_id.lang or self.env.user.lang
            message_body = ticket._get_ticket_reopen_digest(reason, lang=lang)
            try:
                ticket.message_post(body=message_body,message_type='comment')
            except:
                pass
    
    def _create_reopen_ticket_reason(self, ticket, reason):
        reopen_reason_id = self.env['project.ticket.reopen']
        reopen_reason_id.create(ticket._prepare_ticket_reopen_reason_values(ticket, reason))

    def _prepare_ticket_reopen_reason_values(self, ticket, reason):
        if self.env.user.has_group('base.group_portal'):
            reopen_by = 'customer'
        else:
            reopen_by = 'user'
        return {
            'ticket_id': ticket.id,
            'reopen_by': reopen_by,
            'name': reason,
            'date_reopen': fields.Datetime.now(),
        }

    # Ticket Log ----------------
    def _create_ticket_log(self, ticket, old_stage_id, new_stage_id):
        log_id = self.env['project.ticket.log'].create({
            'ticket_id': ticket.id,
            'old_stage_id': old_stage_id.id,
            'new_stage_id': new_stage_id.id,
        })
    # ------------------------------------------------------------------------
    # ------------------------------ actions ---------------------------------
    # ------------------------------------------------------------------------
    def _get_ticket_reopen_digest(self, reason, template='de_helpdesk.project_ticket_reopen_digest', lang=None):
        values = {
                  'reason': reason,
                 }
        return self.env['ir.qweb'].with_context(lang=lang)._render(template, values)

    def _get_ticket_merge_digest(self, ticket, template='de_helpdesk.merge_tickets_digest', lang=None):
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
                'delete': False,
            },
            
        })
        return action

    def open_ticket_history(self):
        action = self.env.ref('de_helpdesk.action_ticket_log').read()[0]
        action.update({
            'name': 'Ticket History',
            'view_mode': 'tree',
            'res_model': 'project.ticket.log',
            'type': 'ir.actions.act_window',
            'domain': [('ticket_id','=',self.id)],
            'context': {
                'create': False,
                'edit': False,
                'delete': False,
            },
            
        })
        return action

    
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
