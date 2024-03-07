# -*- coding: utf-8 -*-

from odoo import models, fields, api

TICKET_PRIORITY = [
    ('0', 'Low priority'),
    ('1', 'Medium priority'),
    ('2', 'High priority'),
    ('3', 'Urgent'),
]

class ProjectSLA(models.Model):
    _name = 'project.sla'
    _description = "Project SLA Policies"
    _order = "name"

    name = fields.Char(required=True, index=True, translate=True)
    description = fields.Html('SLA Policy Description', translate=True)
    active = fields.Boolean('Active', default=True)
    project_id = fields.Many2one('project.project', 'Helpdesk Team', required=True)

    priority = fields.Selection(
        TICKET_PRIORITY, string='Priority',
        default='0', required=True)
    company_id = fields.Many2one('res.company', 'Company', related='project_id.company_id', readonly=True, store=True)
    ticket_count = fields.Integer(compute='_compute_ticket_count')

    # Computed Methods
    def _compute_ticket_count(self):
        for record in self:
            record.ticket_count = 1
            
    # Actions
    def action_open_helpdesk_ticket(self):
        pass