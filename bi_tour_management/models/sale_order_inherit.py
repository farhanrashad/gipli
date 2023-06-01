from odoo import fields, models


class CustomSaleOrder(models.Model):
    _inherit = 'sale.order'

    # Add your custom field(s) here
    tour_book = fields.Char(string='Custom Tour')
