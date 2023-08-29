from odoo import models, fields


class CrimeType(models.Model):
    _name = 'crime.type'
    _description = 'Crime Type'

    name = fields.Char('Name')
    code = fields.Char('Code')
