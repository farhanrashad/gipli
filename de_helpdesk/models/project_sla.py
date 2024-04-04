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

    prj_ticket_type_ids = fields.Many2many(
        'project.ticket.type', 
        string='Types',
         domain="['|',('project_id','=',False),('project_id','=',project_id)]"
    )
    tag_ids = fields.Many2many(
        'project.tags', string='Tags')
    stage_id = fields.Many2one(
        'project.task.type', 'Target Stage',
        help='Minimum stage a ticket needs to reach in order to satisfy this SLA.')
    exclude_stage_ids = fields.Many2many(
        'project.task.type', string='Excluding Stages', copy=True,
        domain="[('id', '!=', stage_id.id)]",
        help="The time spent in these stages won't be taken into account in the calculation of the SLA.")
    partner_ids = fields.Many2many(
        'res.partner', string="Customers")
    company_id = fields.Many2one('res.company', 'Company', related='team_id.company_id', readonly=True, store=True)
    time = fields.Float('Within', default=0, required=True,
        help='Maximum number of working hours a ticket should take to reach the target stage, starting from the date it was created.')
    
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