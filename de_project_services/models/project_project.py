# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjecProject(models.Model):
    _inherit = "project.project"

    is_service_project_template = fields.Boolean('Service Project Template')
    days_completion = fields.Integer(string='Days Completion')

