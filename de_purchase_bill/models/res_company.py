# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    purchase_down_payment_product_id = fields.Many2one(
        comodel_name='product.product',
        string="Downpayment Product",
        domain=[
            ('type', '=', 'service'),
            ('purchase_method', '=', 'purchase'),
        ],
        help="Default product used for down payments",
        check_company=True,
    )
