from odoo import fields, models


class TravelClass(models.Model):
    _name = 'travel.class'
    _description = 'Travel Class'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    transport_type_id = fields.Many2one('product.product', string='Transport Type')
