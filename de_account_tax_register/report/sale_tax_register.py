# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2019-today Dynexcel Business Solution <www.dynexcel.com>

#################################################################################

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError

class SaleTaxRegister(models.AbstractModel):
    _name = 'report.de_account_tax_register.sale_tax_register'
    _description = 'Sale Tax Register Report'
    
    '''Find Sale invoices between the date and find total outstanding amount'''
    @api.model
    def _get_report_values(self, docids ,data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        sale_invoice = []                                               
        if docs.target_move == 'posted':
            invoices = self.env['account.move'].search([('invoice_date', '>=', docs.start_date),('invoice_date', '<=', docs.end_date),
                             ('invoice_line_ids.date', '>=', docs.start_date),('invoice_line_ids.date', '<=', docs.end_date),
                                                        ('journal_id.type','=', 'sale'),('state','=', 'posted')])
        else:
            invoices = self.env['account.move'].search([('invoice_date', '>=', docs.start_date),('invoice_date', '<=', docs.end_date),
                            ('invoice_line_ids.date', '>=', docs.start_date),('invoice_line_ids.date', '<=', docs.end_date),
                                                        ('journal_id.type','=', 'sale')])
                                              
        if invoices:
        #    amount_due = 0
        #    for total_amount in invoices:
        #        amount_due += total_amount.amount_residual
        #    docs.total_amount_due = amount_due

            return {
                'docs': docs,
                'invoices': invoices,
            }
        else:
            raise UserError("There is not any Sale invoice in between selected dates")
            
            
#     def cal_string(invoices.invoice_line_ids.move_id):
#         if len(invoices.invoice_line_ids.move_id) >5
#             val=invoices.invoice_line_ids.move_id[:5]+'...' 
#         else: 
#             val=invoices.invoice_line_ids.move_id
#         return val