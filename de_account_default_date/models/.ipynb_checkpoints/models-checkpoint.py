# -*- coding: utf-8 -*-

import datetime 
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


from odoo.addons import decimal_precision as dp

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    @api.model
    def _get_default_invoice_date(self):
        #last_id = self.env['account.move'].search([])[-1]
        invoice_id = self.invoice_date
        last_rs = last_confirmed_order = self.env['account.move'].search([], order='id desc',limit=1)
        for rs in last_rs:
            invoice_id = rs.invoice_date
        return invoice_id
        #return last_id.invoice_date
        #return datetime.datetime.strptime(last_id.create_date, '%d%m%Y').date()
        #return fields.Date.today()
        #return fields.Date.today() if self._context.get('default_type', 'entry') in ('in_invoice', 'in_refund', 'in_receipt') else False
        
    invoice_date = fields.Date(string='Invoice/Bill Date', readonly=True, index=True, copy=False,
        states={'draft': [('readonly', False)]},
        default=_get_default_invoice_date)