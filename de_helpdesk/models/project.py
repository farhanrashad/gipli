# -*- coding: utf-8 -*-

from odoo import models, fields, api

TICKET_PRIORITY = [
    ('0', 'Low priority'),
    ('1', 'Medium priority'),
    ('2', 'High priority'),
    ('3', 'Urgent'),
]

class Project(models.Model):
    _inherit = 'project.project'

    auto_assignment = fields.Boolean("Automatic Assignment")
    assign_method = fields.Selection([
        ('randomly', 'Each user is assigned an equal number of tickets'),
        ('balanced', 'Each user has an equal number of open tickets')],
        string='Assignment Method', default='randomly', required=True,
        help="New tickets will automatically be assigned to the team members that are available, according to their working hours and their time off.")

    is_sla = fields.Boolean('SLA Policies', default=True)