# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectMilestone(models.Model):
    _inherit = "project.milestone"

    days_completion = fields.Integer(string='Days Completion')

