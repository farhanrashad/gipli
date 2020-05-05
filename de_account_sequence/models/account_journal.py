# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    seq_interval = fields.Selection([
        ('day', 'Daily'),
        ('month', 'Monthly'),
        ('year', 'Yearly')], string='Sequence Interval', default='day', )
