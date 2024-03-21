# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.fields import Command

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'    
    is_downpayment = fields.Boolean(
        string="Is a down payment",
        help="Down payments are made when creating invoices from a sales order."
            " They are not copied when duplicating a sales order.")

    bill_status = fields.Selection(
        selection=[
            ('billed', "Fully Billed"),
            ('to bill', "To Bill"),
            ('no', "Nothing to Bill"),
        ],
        string="Bills Status",
        compute='_compute_bill_status',
        store=True)

    @api.depends('state', 'product_uom_qty', 'qty_received', 'qty_to_invoice', 'qty_invoiced')
    def _compute_bill_status(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if line.state != 'sale':
                line.bill_status = 'no'
            elif line.is_downpayment and line.untaxed_amount_to_invoice == 0:
                line.bill_status = 'billed'
            elif not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                line.bill_status = 'to bill'
            #elif line.state == 'sale' and line.product_id.invoice_policy == 'order' and\
            #        line.product_uom_qty >= 0.0 and\
            #        float_compare(line.qty_delivered, line.product_uom_qty, precision_digits=precision) == 1:
            #    line.bill_status = 'upselling'
            elif float_compare(line.qty_invoiced, line.product_uom_qty, precision_digits=precision) >= 0:
                line.bill_status = 'billed'
            else:
                line.bill_status = 'no'
                
    def _prepare_invoice_line(self, **optional_values):
        """Prepare the values to create the new invoice line for a sales order line.

        :param optional_values: any parameter that should be added to the returned invoice line
        :rtype: dict
        """
        self.ensure_one()
        res = {
            'display_type': self.display_type or 'product',
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [Command.set(self.taxes_id.ids)],
            'purchase_line_id': self.id, #[Command.link(self.id)],
            'is_purchase_downpayment': self.is_downpayment,
        }
        self._set_analytic_distribution(res, **optional_values)
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res

    def _set_analytic_distribution(self, inv_line_vals, **optional_values):
        analytic_account_id = False #self.order_id.analytic_account_id.id
        if self.analytic_distribution and not self.display_type:
            inv_line_vals['analytic_distribution'] = self.analytic_distribution
        if analytic_account_id and not self.display_type:
            analytic_account_id = str(analytic_account_id)
            if 'analytic_distribution' in inv_line_vals:
                inv_line_vals['analytic_distribution'][analytic_account_id] = inv_line_vals['analytic_distribution'].get(analytic_account_id, 0) + 100
            else:
                inv_line_vals['analytic_distribution'] = {analytic_account_id: 100}
    