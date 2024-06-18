# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjecTask(models.Model):
    _inherit = "project.task"

    days_completion = fields.Integer(string='Days Completion')

