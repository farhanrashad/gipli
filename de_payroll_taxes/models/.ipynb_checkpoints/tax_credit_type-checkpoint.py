# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TaxCreditType(models.Model):
    _name = 'tax.credit.type'
    _description = 'Tax Credit Type'
    
    
    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one('res.company', string='Company')
    
    
    

