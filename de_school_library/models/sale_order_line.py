# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, date
from pytz import timezone, UTC

from odoo import api, fields, models, _
from odoo.tools import format_datetime, format_time


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_borrow_order = fields.Boolean(related='order_id.is_borrow_order')
    is_product_book = fields.Boolean(related='product_id.is_book', depends=['product_id'])


    book_pickup_date = fields.Datetime(
        string="Pickup", )
    book_return_date = fields.Datetime(
        string="Return", )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Clean rental related data if new product cannot be rented."""
        if (not self.is_product_book) and self.is_borrow_order:
            self.update({
                'is_borrow_order': False,
                'book_pickup_date': False,
                'book_return_date': False,
            })
       
            
    def schedule_product(self):
        action = {
            'name': _('Rent a Book'),
            'res_model': 'oe.library.fee.config.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'sale.order.line',
                'active_ids': self.ids,
                'active_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
        return action