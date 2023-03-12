# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class HREOSCompRule(models.Model):
    _name = "hr.eos.comp.rule"
    _description = "EOS Compensatin Rules"
    _order = 'name asc'
    
    name = fields.Char(required=True)
    eos_category_ids = fields.Many2many('hr.eos.comp.rule.category', string='Compensation Categories')
    amount_select = fields.Selection([
        ('fix', 'Fixed Amount'),
        ('code', 'Python Code'),
    ], string='Amount Type', index=True, required=True, default='fix', help="The computation method for the rule amount.")
    amount_fix = fields.Float(string='Fixed Amount', digits='Payroll')
    amount_python_compute = fields.Text(string='Python Code',
        default='''
                    # Available variables:
                    #----------------------
                    # payslip: object containing the payslips
                    # employee: hr.employee object
                    # contract: hr.contract object
                    # rules: object containing the rules code (previously computed)
                    # categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
                    # worked_days: object containing the computed worked days.
                    # inputs: object containing the computed inputs.

                    # Note: returned value have to be set in the variable 'result'

                    result = contract.wage * 0.10''')
    

class HREOSCompRuleCategory(models.Model):
    _name = "hr.eos.comp.rule.category"
    _description = "EOS Compensatin Rule Category"
    _order = 'name asc'
    
    name = fields.Char(required=True)
    
