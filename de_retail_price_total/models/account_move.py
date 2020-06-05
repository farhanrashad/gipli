# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class DeAccountMove(models.Model):
    _inherit='account.move'

    @api.depends('invoice_line_ids.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax =retail_price_total= 0.0
            for line in order.invoice_line_ids:
                test = line.quantity * line.sh_retail_price
                retail_price_total += test
            order.update({
                'retail_price_total': retail_price_total,
            })

    retail_price_total = fields.Monetary("Retail Price Total",readonly=True ,compute='_amount_all')
