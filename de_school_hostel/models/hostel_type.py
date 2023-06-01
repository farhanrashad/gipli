from odoo import models, fields


class HostelType(models.Model):
    _name = 'hostel.type'
    _description = 'Hostel Type'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
