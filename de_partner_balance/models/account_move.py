# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


from odoo.addons import decimal_precision as dp

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    #balance = fields.Monetary(string)
    debit = fields.Monetary(related='partner_id.debit', string='Total Receivable', readonly=True,store=False)
    credit = fields.Monetary(related='partner_id.credit', string='Total Payable', readonly=True, store=False)
