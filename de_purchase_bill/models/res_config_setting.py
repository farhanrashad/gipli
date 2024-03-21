# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    purchase_down_payment_product_id = fields.Many2one('product.product', related="company_id.purchase_down_payment_product_id")


    purchase_deposit_product_id = fields.Many2one(
        'product.product',
        'Deposit Product',
        domain="[('type', '=', 'service')]",
        config_parameter='de_purchase_bill.default_purchase_product_id',
        help='Default product used for payment advances')
    
    deposit_default_journal_id = fields.Many2one('account.journal', 'Depoisit Journal', domain="[('type', '=', 'purchase')]", config_parameter='de_purchase_bill.default_deposit_journal_id', help='journal used for default deposit')