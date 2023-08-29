from odoo import models, fields


class TransportCarrier(models.Model):
    _name = 'transport.carrier'
    _description = 'Transport Carrier'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code')
