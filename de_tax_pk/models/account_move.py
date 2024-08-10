# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import frozendict
from odoo.exceptions import ValidationError, UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_gst = fields.Monetary(
        string='GST',
        compute='_compute_gst_wht_amount', store=True, readonly=True,
    )
    amount_gst_signed = fields.Monetary(
        string='GST Signed',
        compute='_compute_gst_wht_amount', store=True, readonly=True,
        currency_field='company_currency_id',
    )
    amount_wht = fields.Monetary(
        string='WHT',
        compute='_compute_gst_wht_amount', store=True, readonly=True,
    )
    amount_wht_signed = fields.Monetary(
        string='WHT Signed',
        compute='_compute_gst_wht_amount', store=True, readonly=True,
        currency_field='company_currency_id',
    )

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
    )
    def _compute_gst_wht_amount(self):
        for move in self:
            total_untaxed, total_untaxed_currency = 0.0, 0.0
            total_tax, total_tax_currency = 0.0, 0.0
            total_wht, total_wht_currency = 0.0, 0.0
            total_residual, total_residual_currency = 0.0, 0.0
            total, total_currency = 0.0, 0.0

            for line in move.line_ids:
                if move.is_invoice(True):
                    # === Invoices ===
                    if line.display_type == 'tax' or (line.display_type == 'rounding' and line.tax_repartition_line_id):
                        # Check if the tax has withholding enabled
                        if line.tax_line_id and line.tax_line_id.withholding:
                            # Withholding Tax amount
                            total_wht += line.balance
                            total_wht_currency += line.amount_currency
                        else:
                            # GST amount (non-withholding tax)
                            total_tax += line.balance
                            total_tax_currency += line.amount_currency
                        
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type in ('product', 'rounding'):
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.display_type == 'payment_term':
                        # Residual amount.
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1

            # Compute amounts
            move.amount_gst = sign * (total_tax_currency - total_wht_currency)
            move.amount_gst_signed = - (total_tax - total_wht)
            move.amount_wht = sign * total_wht_currency
            move.amount_wht_signed = - total_wht
