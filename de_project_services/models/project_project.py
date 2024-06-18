# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjecProject(models.Model):
    _inherit = "project.project"

    days_completion = fields.Integer(string='Days Completion')

