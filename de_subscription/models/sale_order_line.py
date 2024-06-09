# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, date
from odoo import api, fields, models, _
from odoo.tools import float_compare, format_datetime, format_time
from pytz import timezone, UTC
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import relativedelta, format_date


INTERVAL_FACTOR = {
    'day': 30.437,  # average number of days per month over the year,
    'week': 30.437 / 7.0,
    'month': 1.0,
    'year': 1.0 / 12.0,
}

class SubscriptionOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_recurring = fields.Boolean(related="product_template_id.is_recurring")
    amount_monthly_subscription = fields.Monetary(compute='_compute_monthly_subscription', string="Monthly Subscription")
    parent_subscription_line_id = fields.Many2one('sale.order.line', compute='_compute_parent_line', store=True, precompute=True)

    @api.depends('is_recurring', 'price_subtotal')
    def _compute_monthly_subscription(self):
        for line in self:
            if not line.is_recurring or not line.order_id.subscription_plan_id.billing_period:
                line.amount_monthly_subscription = 0
            else:
                line.amount_monthly_subscription = line.price_subtotal * INTERVAL_FACTOR[line.order_id.subscription_plan_id.recurring_interval_type] / line.order_id.subscription_plan_id.recurring_interval
                
    def _compute_parent_line(self):
        parent_line_ids = self.order_id.parent_subscription_id.order_line
        for line in self:
            if not line.product_id.is_recurring:
                continue
            matching_line_ids = parent_line_ids.filtered(
                lambda l:
                (l.order_id, l.product_id, l.product_uom, l.order_id.currency_id, l.order_id.subscription_plan_id,
                 l.order_id.currency_id.round(l.price_unit) if l.order_id.currency_id else round(l.price_unit, 2)) ==
                (line.order_id.parent_subscription_id, line.product_id, line.product_uom, line.order_id.currency_id, line.order_id.subscription_plan_id,
                 line.order_id.currency_id.round(line.price_unit) if line.order_id.currency_id else round(line.price_unit, 2)
                 )
            )
            if matching_line_ids:
                line.parent_subscription_line_id = matching_line_ids.ids[-1]
            else:
                line.parent_subscription_line_id = False
                


    def _get_renew_order_values(self, subscription_id, period_end=None):
        order_lines = []
        description_needed = False
        today = fields.Date.today()
    
        for line in self:
            partner_lang = line.order_id.partner_id.lang
            line = line.with_context(lang=partner_lang) if partner_lang else line
            product = line.product_id
            order_lines.append((0, 0, {
                'parent_subscription_line_id': line.id,
                'name': line.name,
                'product_id': product.id,
                'product_uom': line.product_uom.id,
                'product_uom_qty': 0 if subscription_id.subscription_type == 'upsell' else line.product_uom_qty,
                'price_unit': line.price_unit,
            }))
            description_needed = True
    
        if subscription_id.subscription_type == 'upsell' and description_needed and period_end:
            start_date = max(today, line.order_id.first_contract_date or today)
            end_date = period_end - relativedelta(days=1)
            if start_date >= end_date:
                line_name = _('Recurring products are entirely discounted as the next period has not been invoiced yet.')
            else:
                format_start = format_date(self.env, start_date)
                format_end = format_date(self.env, end_date)
                line_name = _('Recurring products are discounted according to the prorated period from %s to %s') % (format_start, format_end)
    
            order_lines.append((0, 0, {
                'display_type': 'line_note',
                'sequence': 999,
                'name': line_name,
                'product_uom_qty': 0
            }))
    
        return order_lines

    def _reset_subscription_qty_to_invoice(self):
        """ Define the qty to invoice on subscription lines equal to product_uom_qty for recurring lines
            It allows avoiding using the _compute_qty_to_invoice with a context_today
        """
        today = fields.Date.today()
        for line in self:
            if not line.is_recurring or line.product_id.invoice_policy == 'delivery' or line.order_id.date_start and line.order_id.date_start > today:
                continue
            line.qty_to_invoice = line.product_uom_qty

    # Portal actions
    def _get_upsell_order_lines(self, kw):
        order_lines = []
        for key, value in kw.items():
            if key.startswith('product_') and value:
                product_id = int(key.split('_')[1])  # Extract the product ID from the key
                product = self.env['product.product'].sudo().browse(product_id)
                upsell_line_vals = {
                    'product_id': product.id,
                    'name': product.name,
                    'product_uom_qty': 1,  # You can modify this as needed
                    'price_unit': product.list_price,  # Assuming list_price is the price you want to use
                    'tax_id': [(6, 0, product.taxes_id.ids)],  # Assuming taxes_id is the taxes you want to use
                }
                order_lines.append((0, 0, upsell_line_vals))
        return order_lines