# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, date
from odoo import api, fields, models, _
from odoo.tools import float_compare, format_datetime, format_time
from pytz import timezone, UTC
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class SubscriptionOrderLine(models.Model):
    _inherit = 'sale.order.line'


    parent_subscription_line_id = fields.Many2one('sale.order.line', compute='_compute_parent_line_id', store=True, precompute=True)

    def _compute_parent_line_id(self):
        """
        Compute the link between a SOL and the line in the parent order. The matching is done based on several
        fields values like the price_unit, the uom, etc. The method does not depend on pricelist_id or currency_id
        on purpose because '_compute_price_unit' depends on 'parent_line_id' and it triggered side effects
        when we added these dependencies.
        """
        parent_line_ids = self.order_id.new_subscription_id.order_line
        for line in self:
            if not line.order_id.new_subscription_id: #or not line.product_id.recurring_invoice:
                continue
            # We use a rounding to avoid -326.40000000000003 != -326.4 for new records.
            matching_line_ids = parent_line_ids.filtered(
                lambda l:
                (l.order_id, l.product_id, l.product_uom, l.order_id.currency_id, l.order_id.subscription_plan_id,
                 l.order_id.currency_id.round(l.price_unit) if l.order_id.currency_id else round(l.price_unit, 2)) ==
                (line.order_id.new_subscription_id, line.product_id, line.product_uom, line.order_id.currency_id, line.order_id.subscription_plan_id,
                 line.order_id.currency_id.round(line.price_unit) if line.order_id.currency_id else round(line.price_unit, 2)
                 )
            )
            if matching_line_ids:
                line.parent_subscription_line_id = matching_line_ids.ids[-1]
            else:
                line.parent_subscription_line_id = False
                

    def _get_renew_order_values(self, subscription_state, period_end=None):
        order_lines = []
        description_needed = False #self._need_renew_discount_info()
        today = fields.Date.today()
        for line in self:
            #if not line.recurring_invoice:
            #    continue
            partner_lang = line.order_id.partner_id.lang
            line = line.with_context(lang=partner_lang) if partner_lang else line
            product = line.product_id
            order_lines.append((0, 0, {
                'parent_subscription_line_id': line.id,
                'name': line.name,
                'product_id': product.id,
                'product_uom': line.product_uom.id,
                'product_uom_qty': 0 if subscription_state == '7_upsell' else line.product_uom_qty,
                'price_unit': line.price_unit,
            }))
            description_needed = True

        if subscription_state == '7_upsell' and description_needed and period_end:
            start_date = max(today, line.order_id.first_contract_date or today)
            end_date = period_end - relativedelta(days=1)  # the period ends the day before the next invoice
            if start_date >= end_date:
                line_name = _('Recurring products are entirely discounted as the next period has not been invoiced yet.')
            else:
                format_start = format_date(self.env, start_date)
                format_end = format_date(self.env, end_date)
                line_name = _('Recurring products are discounted according to the prorated period from %s to %s', format_start, format_end)

            order_lines.append((0, 0,
                {
                    'display_type': 'line_note',
                    'sequence': 999,
                    'name': line_name,
                    'product_uom_qty': 0
                }
            ))

        return order_lines