# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, date
from pytz import timezone, UTC

from odoo import api, fields, models, _
from odoo.tools import format_datetime, format_time


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_borrow_order = fields.Boolean(related='order_id.is_borrow_order')
    is_product_rentable = fields.Boolean(related='product_id.is_book', depends=['product_id'])