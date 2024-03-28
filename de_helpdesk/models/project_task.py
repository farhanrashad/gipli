# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, tools, _
from datetime import datetime, timedelta

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

    #Customer Rating
    allow_customer_rating = fields.Boolean(related='project_id.allow_customer_rating')
    rating = fields.Selection(
        [('1', 'Poor'), ('2', 'Fair'), ('3', 'Average'), ('4', 'Good'), ('5', 'Excellent')],
        string='Rating'
    )
    rating_comment = fields.Text(string='Rating Comment')
    rating_score = fields.Integer(string='Rating Scroe', compute='_compute_customer_rating')

    
    # Computed Methods
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


    # Action Methods
    # CRUD 
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
        
class ProjectTaskSLALine(models.Model):
    _name = 'project.task.sla.line'
    _description = "Task SLA Line"
    _order = 'date_deadline ASC'
    _rec_name = 'prj_sla_id'

    task_id = fields.Many2one('project.task', string='Ticket', required=True, ondelete='cascade', index=True)
    prj_sla_id = fields.Many2one('project.sla', string='SLA', required=True, ondelete='cascade')
    date_deadline = fields.Datetime("Deadline", compute='_compute_deadline', compute_sudo=True, store=True)
    
    status = fields.Selection([
        ('failed', 'Failed'), 
        ('reached', 'Reached'), 
        ('ongoing', 'Ongoing')
    ], string="Status", 
        compute='_compute_status', compute_sudo=True, search='_search_status')
    
    exceeded_hours = fields.Float("Exceeded Working Hours", compute='_compute_exceeded_hours', compute_sudo=True, store=True, help="Working hours exceeded for reached SLAs compared with deadline. Positive number means the SLA was reached after the deadline.")

    @api.model
    def _search_status(self, operator, value):
        """ Supported operators: '=', 'in' and their negative form. """
        # constants
        datetime_now = fields.Datetime.now()
        positive_domain = {
            'failed': ['|', '&', ('reached_datetime', '=', True), ('deadline', '<=', 'reached_datetime'), '&', ('reached_datetime', '=', False), ('deadline', '<=', fields.Datetime.to_string(datetime_now))],
            'reached': ['&', ('reached_datetime', '=', True), ('reached_datetime', '<', 'deadline')],
            'ongoing': ['|', ('deadline', '=', False), '&', ('reached_datetime', '=', False), ('deadline', '>', fields.Datetime.to_string(datetime_now))]
        }
        # in/not in case: we treat value as a list of selection item
        if not isinstance(value, list):
            value = [value]
        # transform domains
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            # "('status', 'not in', [A, B])" tranformed into "('status', '=', C) OR ('status', '=', D)"
            domains_to_keep = [dom for key, dom in positive_domain if key not in value]
            return expression.OR(domains_to_keep)
        else:
            return expression.OR(positive_domain[value_item] for value_item in value)
