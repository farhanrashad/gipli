# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    purchase_down_payment_product_id = fields.Many2one('product.product', related="company_id.purchase_down_payment_product_id", readonly=False)