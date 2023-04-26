# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SalaryRuleCategory(models.Model):
    _inherit = 'hr.salary.rule.category'
    
    is_compute_tax = fields.Boolean(string='Include in Tax Computation')
    
    
    
    