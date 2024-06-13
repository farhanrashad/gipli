# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _
from odoo.exceptions import UserError, AccessError

class Expenses(models.Model):
    _name = 'xpl.expense'
    _description = 'Xpendless Expense'
    _order = "name desc, id desc"

    name = fields.Char(string='Name', required=True, readonly=False)
    date = fields.Datetime(string='Date', required=True)
    partner_id = fields.Many2one('res.partner', string='Employee', required=True)
    state = fields.Selection([
        ('draft', 'Draft'), 
        ('verified', 'Verified'), 
        ('active', 'Active')], 
        string='Status',default='draft', required=True
    )
    xpl_id = fields.Char(string='XPL ID', required=True, readonly=True)
