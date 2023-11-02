# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
import math
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _, _lt
from odoo.exceptions import ValidationError
from odoo.tools import format_amount, float_compare, float_is_zero

# For our use case: pricing depending on the duration, the values should be sufficiently different from one plan to
# another to not suffer from the approcimation that all months are 31 longs.
# otherwise, 31 days would result in 2 month.
PERIOD_RATIO = {
    'hour': 1,
    'day': 24,
    'week': 24 * 7,
    'month': 24*31, # average number of days per month over the year
    'year': 24*31*12,
}


class ProductLibraryFees(models.Model):
    """ Library Fees """
    _name = 'oe.library.product.fees'
    _description = 'Library Pricing'
    _order = 'product_template_id,price,pricelist_id,library_fee_period_id'

    name = fields.Char(compute='_compute_name')
    description = fields.Char(compute='_compute_description')
    library_fee_period_id = fields.Many2one('oe.library.fees.period', string='Recurrency', required=True)
    price = fields.Monetary(string="Price", required=True, default=1.0)
    currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency_id', store=True)
    product_template_id = fields.Many2one('product.template', string="Product Templates", ondelete='cascade',
                                          help="Select products on which this pricing will be applied.")
    product_variant_ids = fields.Many2many('product.product', string="Product Variants",
                                           help="Select Variants of the Product for which this rule applies. Leave empty if this rule applies for any variant of this template.")
    pricelist_id = fields.Many2one('product.pricelist', ondelete='cascade')
    company_id = fields.Many2one('res.company', related='pricelist_id.company_id')

    #@api.depends('duration', 'unit')
    def _compute_name(self):
        for record in self:
            if not record.name:
                record.name = 'hello' #_("%s %s", record.duration, record.unit)

    def _compute_description(self):
        for pricing in self:
            description = ""
            if pricing.currency_id.position == 'before':
                description += format_amount(self.env, amount=pricing.price, currency=pricing.currency_id)
            else:
                description += format_amount(self.env, amount=pricing.price, currency=pricing.currency_id)
            description += _("/%s", pricing.library_fee_period_id.unit)
            pricing.description = description


