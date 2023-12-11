# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    # Library Inventory

    library_loc_id = fields.Many2one(
        "stock.location", string="In rent",
        domain=[('usage', '=', 'internal')],
        help="This technical location serves as stock for products currently in rental"
        "This location is internal because products in rental"
        "are still considered as company assets.")

    book_charge_product_id = fields.Many2one(
        'product.product', string="Product",
        help="The product is used to add the book fine to the sales order",
        domain="[('type', '=', 'service')]")

    def _create_library_location(self):
        for company in self.sudo():
            if not company.library_loc_id:
                company.library_loc_id = self.env['stock.location'].sudo().create({
                    "name": "Borrow",
                    "usage": "internal",
                    "company_id": company.id,
                })
