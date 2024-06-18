# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectMilestone(models.Model):
    _inherit = "project.milestone"

    is_service_project_template = fields.Boolean(related='project_id.is_service_project_template')
    days_completion = fields.Integer(string='Days Completion')

