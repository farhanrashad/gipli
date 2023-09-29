# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_repayment_mode = fields.Selection(related='company_id.default_repayment_mode', string="Re-Payment Mode", readonly=False, default_model="hr.loan.type")
    default_repayment_product_id = fields.Many2one('product.product', 
            related='company_id.default_repayment_product_id', 
            readonly=False, string="Product", default_model="hr.loan.type")
