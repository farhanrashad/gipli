# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2019-today Ascetic Business Solution <www.dynexcel.com>

#################################################################################

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError

class PurchaseTaxRegister(models.AbstractModel):
    _name = 'report.de_account_tax_register.purchase_tax_register'
    _description = 'Purchase Tax Register Report'

    '''Find Purchase invoices between the date and find total outstanding amount'''
    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        outstanding_invoice = []       
        
        if docs.target_move == 'posted':
            invoices = self.env['account.move'].search([('date', '>=', docs.start_date),('date', '<=', docs.end_date),('journal_id.type','=', 'purchase'),('state','=', 'posted')])
        else:
            invoices = self.env['account.move'].search([('date', '>=', docs.start_date),('date', '<=', docs.end_date),('journal_id.type','=', 'purchase')])
            
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
            raise UserError("There is not any Purchase invoice in between selected dates")

            
    