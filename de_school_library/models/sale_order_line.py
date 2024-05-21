# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, date
from pytz import timezone, UTC

from odoo import api, fields, models, _
from odoo.tools import format_datetime, format_time
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_borrow_order = fields.Boolean(related='order_id.is_borrow_order')
    is_product_book = fields.Boolean(related='product_id.is_book', depends=['product_id'])
    borrow_status = fields.Selection(related='order_id.borrow_status')

    book_pickup_date = fields.Datetime(
        string="Pickup", )
    book_return_date = fields.Datetime(
        string="Return", )

    book_issue_date = fields.Datetime(string='Issue Date',
            default=lambda s: fields.Datetime.now() + relativedelta(minute=0, second=0, hours=1))
    book_return_date = fields.Datetime(string="Return Date",
            default=lambda s: fields.Datetime.now() + relativedelta(minute=0, second=0, hours=1, days=1))
    duration = fields.Integer(
        string="Duration", compute="_compute_book_duration",
        help="The duration unit is based on the unit of the rental pricing rule.")
    duration_unit = fields.Selection([("hour", "Hours"), ("day", "Days"), ("week", "Weeks"), ("month", "Months"), ('year', "Years")],
                                     string="Unit", required=True, compute="_compute_book_duration")

    book_pricing_id = fields.Many2one('lib.product.fees', compute="_compute_book_pricing",
        string="Pricing", help="Best Pricing Rule based on duration")

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    book_qty_returned = fields.Float("Returned", default=0.0, copy=False)
    
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