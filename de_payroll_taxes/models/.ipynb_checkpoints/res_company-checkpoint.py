# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    fiscal_month = fields.Many2one('fiscal.year.month', string='Fiscal Year', ondelete='cascade')
    fiscalyear_last_day = fields.Integer(string='Days', default=30)
    pf_percent = fields.Float(string='Pf Percent(%)')
    pf_exceeding_amt = fields.Float(string='PF Exceeding Amount')
    
    

