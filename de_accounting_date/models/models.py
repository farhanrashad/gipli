# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountingDate(models.Model):
    _inherit = 'account.move'

    # date1 = fields.Date(string="date1", required=False, )

    @api.onchange('invoice_date')
    def _onchange_accounting_date(self):
        """ Make entry on email and availability on change of partner_id field. """
        self.date = self.invoice_date
