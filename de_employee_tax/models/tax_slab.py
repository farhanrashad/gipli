from odoo import models, fields


class TaxSlab(models.Model):
    _name = 'tax.slabs'
    _description = 'Tax Slabs'

    name = fields.Char(string='Tax Slab Description')
    tax_percent = fields.Float(string='Tax % Applied')
    applied_from = fields.Float(string='Applied From')
    applied_to = fields.Float(string='Applied To')
