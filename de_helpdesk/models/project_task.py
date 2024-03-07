# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, tools, _

class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_sla = fields.Boolean(related='project_id.is_sla')
    sla_date_deadline = fields.Datetime("SLA Deadline", compute='_compute_all_sla_deadline', compute_sudo=True, store=True)
    sla_hours_deadline = fields.Float("Hours to SLA Deadline", compute='_compute_all_sla_deadline', compute_sudo=True, store=True)

    domain_user_ids = fields.Many2many('res.users', compute='_compute_domain_from_project')
    prj_ticket_type_id = fields.Many2one('project.ticket.type', string="Type", tracking=True)

    partner_phone = fields.Char(string='Customer Phone', compute='_compute_phone_from_partner', inverse="_compute_inverse_phone_from_partner", store=True, readonly=False)
    partner_email = fields.Char(string='Customer Email', compute='_compute_email_from_partner', inverse="_inverse_partner_email", store=True, readonly=False)

    is_update_partner_email = fields.Boolean('Partner Email will Update', compute='_compute_is_update_partner_email')
    is_update_partner_phone = fields.Boolean('Partner Phone will Update', compute='_compute_is_update_partner_phone')


    # Computed Methods
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