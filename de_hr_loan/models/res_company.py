# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'

    default_repayment_mode = fields.Selection([
        ('credit_memo', 'By Credit Memo'),
        ('payslip', 'By Payslip')
    ], string='Re-Payment Mode', required=True, default='credit_memo')
    default_repayment_product_id = fields.Many2one('product.product', string="Product", required=True, domain="[('type','=','service')]")