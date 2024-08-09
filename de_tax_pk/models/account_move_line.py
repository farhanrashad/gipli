# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import frozendict


class AccounMoveLine(models.Model):
    _inherit = 'account.move.line'

    wht_tax_ids = fields.Many2many(
        comodel_name='account.tax',
        relation='rel_move_line_account_tax',  # Custom relation table name
        column1='move_line_id',              # First column (referring to current model)
        column2='tax_id',              # Second column (referring to account.tax model)
        string="Withholding",
        compute='_compute_wht_tax_ids', store=True, readonly=False, precompute=True,
        context={'active_test': False},
        check_company=True,
    )
    wht_tax_key = fields.Binary(compute='_compute_wht_tax_key', exportable=False)


    @api.depends('tax_ids', 'currency_id', 'partner_id', 'account_id', 'group_tax_id', 'analytic_distribution')
    def _compute_tax_key(self):
        for line in self:
            if line.tax_repartition_line_id:
                line.tax_key = frozendict({
                    'tax_repartition_line_id': line.tax_repartition_line_id.id,
                    'group_tax_id': line.group_tax_id.id,
                    'account_id': line.account_id.id,
                    'currency_id': line.currency_id.id,
                    'analytic_distribution': line.analytic_distribution,
                    'tax_ids': [(6, 0, line.tax_ids.ids)],
                    'tax_tag_ids': [(6, 0, line.tax_tag_ids.ids)],
                    'partner_id': line.partner_id.id,
                    'move_id': line.move_id.id,
                    'display_type': line.display_type,
                })
            else:
                line.wht_tax_key = frozendict({'id': line.id})
                
    @api.depends('product_id', 'product_uom_id')
    def _compute_wht_tax_ids(self):
        for line in self:
            if line.display_type in ('line_section', 'line_note', 'payment_term'):
                continue
            # /!\ Don't remove existing taxes if there is no explicit taxes set on the account.
            if line.product_id:
                line.tax_ids = line._get_computed_withholding_taxes()

    def _get_computed_withholding_taxes(self):
        self.ensure_one()

        if self.move_id.is_sale_document(include_receipts=True):
            # Out invoice.
            if self.product_id.taxes_id:
                tax_ids = self.product_id.taxes_id.filtered(lambda tax: tax.company_id == self.move_id.company_id)
            else:
                tax_ids = self.account_id.tax_ids.filtered(lambda tax: tax.type_tax_use == 'sale')
            if not tax_ids and self.display_type == 'product':
                tax_ids = self.move_id.company_id.account_sale_tax_id
        elif self.move_id.is_purchase_document(include_receipts=True):
            # In invoice.
            if self.product_id.supplier_taxes_id:
                tax_ids = self.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == self.move_id.company_id)
            else:
                tax_ids = self.account_id.tax_ids.filtered(lambda tax: tax.type_tax_use == 'purchase')
            if not tax_ids and self.display_type == 'product':
                tax_ids = self.move_id.company_id.account_purchase_tax_id
        else:
            # Miscellaneous operation.
            tax_ids = False if self.env.context.get('skip_computed_taxes') else self.account_id.tax_ids

        if self.company_id and tax_ids:
            tax_ids = tax_ids.filtered(lambda tax: tax.company_id == self.company_id)

        if tax_ids and self.move_id.fiscal_position_id:
            tax_ids = self.move_id.fiscal_position_id.map_tax(tax_ids)

        return tax_ids

    @api.onchange('wht_tax_ids')
    def _onchange_wht_tax_ids(self):
        if self.wht_tax_ids:
            self._create_tax_move_lines()

    def _create_tax_move_lines(self):
        """Create account.move.line records for the added taxes."""
        move_line_vals = []
        for tax in self.wht_tax_ids:
            move_line_vals.append({
                'move_id': self.id,
                'name': tax.name,
                'account_id': tax.account_id.id,  # Assuming tax has an account_id field
                'debit': 0.0,                    # Adjust the amounts as needed
                'credit': 0.0,                   # Adjust the amounts as needed
                'tax_ids': [(6, 0, [tax.id])],
            })

        if move_line_vals:
            self.env['account.move.line'].create(move_line_vals)


    