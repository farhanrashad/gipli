from odoo import models, fields


class RoomType(models.Model):
    _name = 'room.type'
    _description = 'Room Types'

    name = fields.Char(string='Name')
    room_type_id = fields.Many2one('product.product', string='Room Type')
