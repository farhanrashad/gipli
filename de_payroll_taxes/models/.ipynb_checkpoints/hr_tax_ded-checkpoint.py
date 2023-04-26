# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrTaxDed(models.Model):
    _name = 'hr.tax.ded'
    _description = 'HR Tax Deduction'
    
    _rec_name='employee_id'
    
    
    date = fields.Date(string='Date') 
    tax_year = fields.Char(string='Year')
    period_num = fields.Integer(string='Period Number') 
    employee_id = fields.Many2one('hr.employee', string='Employee')
    fiscal_month = fields.Many2one('fiscal.year.month', string='Month')
    taxable_amount = fields.Float(string='Taxable Amount')
    pf_amount = fields.Float(string='PF Amount')
    tax_ded_amount = fields.Float(string='Tax Deduct Amount')
    company_id = fields.Many2one('res.company', string='Company')
    
    
    @api.constrains('date')
    def _check_date(self):
        for line in self:
            if line.date:
                line.update({
                    'tax_year': line.date.year,
                    'fiscal_month': line.date.month,
                })
    
    
    
    
    
    

