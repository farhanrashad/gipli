# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountPaymentRequest(models.Model):
    _name = 'account.payment.request'
    _description = 'Account Payment Request'
    
    
    name = fields.Char(string='Name')
    payment_type = fields.Char(string='Payment Type') 
    account_id = fields.Many2one('account.account', string='Account', required=True)
    rule_id = fields.Many2one('hr.salary.rule', string='Rule', required=True)
    amount = fields.Float(string='Amount')
    fiscal_month = fields.Many2one('fiscal.year.month', string='Month')
    year = fields.Char(string='Year')
    company_id = fields.Many2one('res.company', string='Company')
    
    
    
    
    
    

