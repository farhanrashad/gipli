from odoo import models, fields


class TransportInformation(models.Model):
    _name = 'transport.information'
    _description = 'Transport Information'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='Service Provider ')
    transport_type_info_ids = fields.One2many('transport.type.info', 'transport_id', string='Transport Type Info')
    rcv_account_id = fields.Many2one('account.account', string='Receivable Account', required=True)
    pay_account_id = fields.Many2one('account.account', string='Payable Account', required=True)

    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'),
                   ('confirm', 'Confirm'), ],
        required=False, default='draft')

    def confirm_transport_info(self):
        for rec in self:
            rec.state = 'confirm'


class TransportTypeInfo(models.Model):
    _name = 'transport.type.info'
    _description = 'Transport Type Info'

    transport_id = fields.Many2one('transport.information', string='Transport')
    name = fields.Char(string='Description')
    transport_carrier_id = fields.Many2one('transport.carrier', string='Carrier Name')
    transport_type_id = fields.Many2one('product.product', string='Transport Type')
    transport_class_id = fields.Many2one('travel.class', string='Travel Class')
    from_dest_id = fields.Many2one('tour.destination', string='From Destination')
    to_dest_id = fields.Many2one('tour.destination', string='To Destination')
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    cost_price_adult = fields.Float(string='Cost Price (Adult)')
    sale_price_adult = fields.Float(string='Sale Price (Adult)')
    cost_price_child = fields.Float(string='Cost Price (Child)')
    sale_price_child = fields.Float(string='Sale Price (Child)')
