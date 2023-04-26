# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SalaryRuleCategory(models.Model):
    _inherit = 'hr.payslip.input.type'
    
    is_arrears = fields.Boolean(string='Arrears')
    is_bonus = fields.Boolean(string='Bonus')
    is_include_tax = fields.Boolean(string='Is Include Tax')
    
    
    