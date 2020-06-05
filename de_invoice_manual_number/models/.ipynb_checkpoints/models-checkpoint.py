# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


from odoo.addons import decimal_precision as dp

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    manual_number = fields.Integer(string='Manual Invoice Number', states={'cancel': [('readonly', True)], 'posted': [('readonly', True)]})
    
    #def write(self,vals):
        #res = super(AccountMove,self).write(vals)
        #if self.journal_id.type == 'sale' or self.journal_id.type == 'purchase':
            #self.update({
            #    'invoice_sequence_number_next':self.manual_number
            #})
        #return res
    
    #@api.onchange('journal_id','invoice_date')
    #def manual_number_change(self):
        #self.write({
            #'manual_number':self.journal_id.sequence_number_next,
        #})