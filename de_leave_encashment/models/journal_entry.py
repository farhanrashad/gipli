# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class JournalEntry(models.Model):
    _name = 'journal.entry'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    number = fields.Char(string='Number')
    app = fields.Boolean(default=False)
    due_date = fields.Date(string='Due Date')
    next_activity = fields.Char(string='Next Activity')
    tax_excluded_total = fields.Float(string='Tax Excluded Total')
    total = fields.Float(string='Total')
    payment_status = fields.Selection([
        ('paid', 'Paid'),
        ('unpaid', 'Un Paid')], string='Payment Status', default='unpaid')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled')
    ], string='State', default='draft')

    def action_paid(self):
        self.app = True
        self.write({'payment_status': 'paid'})

    def action_unpaid(self):
        self.app = True
        self.write({'payment_status': 'unpaid'})
