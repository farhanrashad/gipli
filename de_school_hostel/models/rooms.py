from odoo import models, fields, api
from odoo.exceptions import AccessDenied, AccessError, MissingError, UserError, ValidationError


class HostelRoom(models.Model):
    _name = 'oe.school.hostel.room'
    _description = 'Hostel Room'
    _rec_name = 'total_rooms'

    product_id = fields.Many2one('product.product', string='Product', required=True,
                                 domain=[('is_hostel_room', '=', True)])
    hostel_id = fields.Many2one('oe.school.hostel', string='Hostel', required=True)
    capacity = fields.Integer(string='Capacity', required=True)
    total_rooms = fields.Integer(string='Total Rooms', required=True)

    @api.constrains('product_id')
    def _check_is_hostel_room(self):
        for room in self:
            if not room.product_id.is_hostel_room:
                raise ValidationError('Only products available having Is Hostel Room true can be selected.')

    @api.model
    def create(self, vals):
        room = super().create(vals)
        for i in range(room.total_rooms):
            self.env['stock.lot'].create({
                'product_id': room.product_id.id,
                'company_id': self.env.company.id,
                'hostel_id': room.hostel_id.id,
            })
        return room
