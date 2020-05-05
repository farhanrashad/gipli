# -*- coding: utf-8 -*-

from odoo import models, fields, api
#import datetime
from datetime import datetime

class AccountMove(models.Model):
    _inherit = 'account.move'

    seq_number = fields.Integer(string='SEQ. Number', store=True,readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    seq_name = fields.Char(string='Sequence', store=True,readonly=True,copy=False, states={'draft': [('readonly', False)]} )
    #@api.depends('journal_id','invoice_date')
    @api.onchange('invoice_date','date')
    def _onchange_invoice_date(self):
        for invoice in self:
            am_obj = self.env['account.move']
            domain = d = ''
            date = ''
            if invoice.journal_id.type in ('sale','purchase'):
                date = invoice.invoice_date
            else:
                date = invoice.date
            
            if date:
                if invoice.journal_id.seq_interval == 'day':
                    domain = [('journal_id', '=', invoice.journal_id.id),('date', '=', date),]
                    d = date.strftime("%d%m%y")
                elif invoice.journal_id.seq_interval == 'year':
                    domain = [('journal_id', '=', invoice.journal_id.id)]
                    d = date.strftime("%Y")
            
                where_query = am_obj._where_calc(domain)
                am_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT max(coalesce(seq_number,0))+1 from " + from_clause + " where " + where_clause                
                self.env.cr.execute(select, where_clause_params)
                invoice.seq_number = self.env.cr.fetchone()[0] or 1
            
                invoice.seq_name = invoice.journal_id.code + '/' + d + '/' + str(invoice.seq_number).rjust(5, '0')
                
    
