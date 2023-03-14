from odoo import fields, models, _


class ShiptType(models.Model):
    _name = 'shipt.type'
    _description = 'Shipt Type'

    name = fields.Char(string='Name', required=True)
    time_from = fields.Float(string='Time From', required=True)
    time_to = fields.Float(string='Time To', required=True)

