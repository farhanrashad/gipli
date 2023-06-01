from odoo import fields, models


class HotelType(models.Model):
    _name = 'hotel.type'
    _description = 'Hotel Type'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
