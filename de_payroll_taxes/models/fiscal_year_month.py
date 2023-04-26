# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FiscalYearMonth(models.Model):
    _name = 'fiscal.year.month'
    _description='Fiscal Year Month'
    
    name=fields.Char(string='Name')
    days = fields.Integer(string='Days')
    
    
    
    
    

