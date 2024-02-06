# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class product_template(models.Model):
    _inherit = "product.template"

    is_recurring = fields.Boolean(
        'Subscription Product',
        help='If set, confirming a sale order with this product will create a subscription')