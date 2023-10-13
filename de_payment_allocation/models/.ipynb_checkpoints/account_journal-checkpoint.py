# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError

class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    allow_payment_reconcile = fields.Boolean('Allow Reconciliation On Payment', default=True)
    is_clearing = fields.Boolean('Is Clearing Journal', default=False)
    