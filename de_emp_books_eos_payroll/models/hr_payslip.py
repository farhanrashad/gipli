# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips, ResultRules
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    #input_line_ids = fields.One2many(compute='_compute_eos_input_line_ids', store=True, readonly=False, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    eos_contract_id = fields.Many2one('hr.eos.contract', string='End of Services Contract',)
    hr_employee_eos_comp_lines = fields.One2many('hr.eos.comp.line', 'payslip_id', string='Compensation Lines')
    comp_count = fields.Integer(compute='_compute_comp_count', string='Compensations')
    
    @api.depends('hr_employee_eos_comp_lines', 'hr_employee_eos_comp_lines.payslip_id')
    def _compute_comp_count(self):
        for payslip in self:
            payslip.comp_count = len(payslip.mapped('hr_employee_eos_comp_lines'))
            

    
    @api.onchange('eos_contract_id')
    def _onchange_eos_contract_id(self):
        if not self.eos_contract_id:
            return
        
        input_lines_vals = []
        eos_contract = self.eos_contract_id
        self.employee_id = eos_contract.employee_id.id
        self.struct_id = eos_contract.struct_id.id
        self.date_from = fields.Date.to_string(eos_contract.last_payslip_id.date_to + timedelta(1))  
        self.date_to = eos_contract.date_notice_end
        
        self.hr_employee_eos_comp_lines = self.env['hr.eos.comp.line'].search([
                ('employee_id', '=', eos_contract.employee_id.id),
                ('eos_contract_id.state', '=', 'approval2'),
            ])
        for payslip in self:
            for input_line in payslip.hr_employee_eos_comp_lines:
                input_lines_vals.append((0, 0, {
                    'amount': input_line.total_amount,
                    'input_type_id': input_line.comp_rule_id.input_type_id.id
                }))
            payslip.update({'input_line_ids': input_lines_vals})
            
    
    #@api.depends('hr_employee_eos_comp_lines')
    def _compute_eos_input_line_ids(self):
        input_lines_vals = []
        for payslip in self:
            #total = sum(payslip.hr_employee_loan_lines.mapped('amount_emi'))
            #lines_to_keep = payslip.eos_input_line_ids.filtered(lambda x: x.input_type_id != loan_type)
            #input_lines_vals = [(5, 0, 0)] + [(4, line.id, False) for line in lines_to_keep]
            for input_line in payslip.hr_employee_eos_comp_lines:
                input_lines_vals.append((0, 0, {
                    'amount': total_amount,
                    'input_type_id': input_line.comp_rule_id.input_type_id.id
                }))
            payslip.update({'input_line_ids': input_lines_vals})
            
    def open_compensations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('End of Service'),
            'res_model': 'hr.eos.comp.line',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.hr_employee_eos_comp_lines.mapped('eos_contract_id').ids)],
        }
        