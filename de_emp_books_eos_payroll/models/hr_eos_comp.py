# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class HREOSCompRule(models.Model):
    _inherit = "hr.eos.comp.rule"
    
    input_type_id = fields.Many2one('hr.payslip.input.type', string='Other Input type')