# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero


class HREOSContract(models.Model):
    _inherit = "hr.eos.contract"
    
    payslip_id = fields.Many2one('hr.payslip', string='Payslip', ondelete='restrict', copy=False, readonly=True)
    last_payslip_id = fields.Many2one('hr.payslip', string='Last Payslip', compute='_compute_last_payslip')
    struct_id = fields.Many2one('hr.payroll.structure', string='Structure',)
    
    def _compute_last_payslip(self):
        payslip = self.env['hr.payslip'].search([('employee_id','=',self.employee_id.id),('state','=','done')],order="date_to desc", limit=1)
        self.last_payslip_id = payslip.id
        
class HREOSCompLine(models.Model):
    _inherit = "hr.eos.comp.line"
    
    payslip_id = fields.Many2one('hr.payslip', string='Payslip', ondelete='restrict', copy=False, readonly=True)
    

