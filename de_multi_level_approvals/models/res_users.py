# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class ResUsers(models.Model):
    _inherit = 'res.users'
    sequence = fields.Integer(string='Sequence')
    department_id = fields.Many2one(related='employee_id.department_id')
    job_title = fields.Char(related='employee_id.job_title')