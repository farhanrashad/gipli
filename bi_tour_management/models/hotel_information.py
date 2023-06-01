from odoo import models, fields, api


class HotelInformation(models.Model):
    _name = 'hotel.information'
    _description = 'Hotel Information'
    _rec_name = 'hotel_partner_id'

    hotel_partner_id = fields.Many2one('res.partner', string='Hotel Partner', required=True)
    hotel_type_id = fields.Many2one('hotel.type', string='Hotel Type', required=True)
    rcv_account_id = fields.Many2one('account.account', string='Receivable Account', required=True)
    pay_account_id = fields.Many2one('account.account', string='Payable Account', required=True)
    hotel_image_1 = fields.Binary(string='Hotel Image 1')
    hotel_image_2 = fields.Binary(string='Hotel Image 2')
    hotel_image_3 = fields.Binary(string='Hotel Image 3')
    room_info_ids = fields.One2many('room.info', 'hotel_id', string='Room Information')
    hotel_service_ids = fields.One2many('hotel.service', 'hotel_id', string='Hotel Services')
    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'),
                   ('confirm', 'Confirm'), ],
        required=False, default='draft')

    def confirm_info(self):
        for rec in self:
            rec.state = 'confirm'


class RoomInfo(models.Model):
    _name = 'room.info'
    _description = 'Room Info'

    room_type_id = fields.Many2one('room.type', string='Room Type')
    hotel_id = fields.Many2one('hotel.information', string='Hotel')
    name = fields.Text(string='Description')
    cost_price = fields.Float(string='Cost Price')
    sale_price = fields.Float(string='Sale Price')


class HotelService(models.Model):
    _name = 'hotel.service'
    _description = 'Hotel Service'

    name = fields.Text(string='Description')
    hotel_id = fields.Many2one('hotel.information', string='Hotel')
    service_id = fields.Many2one('service.type', string='Service')
    cost_price = fields.Float(string='Cost Price')
    product_uom = fields.Many2one('uom.uom', string='Product UoM')
