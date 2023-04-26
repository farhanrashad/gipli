# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrTaxSlide(models.Model):
    _name = 'hr.tax.range'
    _description='HR Tax Range'
    
    name= fields.Char(string='Description')
    date = fields.Date(string='Date', required=True)
    month = fields.Many2one('fiscal.year.month', string='Month')
    year = fields.Char(string='Year')
    tax_range_line_ids = fields.One2many('hr.tax.range.line', 'range_id', string='Tax Range Line')
            
    @api.constrains('date')
    def _check_date(self):
        for line in self:
            if line.date:
                line.update({
                    'name': 'Tax Range For Year '+str(line.date.year),
                    'month': line.date.month,
                    'year': line.date.year,
                })
                for range_line in line.tax_range_line_ids:
                    range_line.update({
                        'month' : line.date.month,
                        'year': line.date.year,
                    })
    
    
class HrTaxSlide(models.Model):
    _name = 'hr.tax.range.line'
    _description='HR Tax Range Line'
    
    range_id = fields.Many2one('hr.tax.range', string='Range')
    month = fields.Many2one('fiscal.year.month', string='Month')
    year = fields.Char(string='Year')                
    start_amount=fields.Float(string='Start Amount', digits=(12, 0))
    end_amount=fields.Float(string='End Amount', digits=(12, 0))
    addition_amount = fields.Float(string='Addition Amount', digits=(12, 0))
    percentage = fields.Integer(string='Percentage(%)')
    deduction_amount = fields.Float(string='Access Over Amount', digits=(12, 0))
