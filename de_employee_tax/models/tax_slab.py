from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TaxSlab(models.Model):
    _name = 'tax.slabs'
    _description = 'Tax Slabs'

    name = fields.Char(string='Tax Slab Description')
    tax_percent = fields.Float(string='Tax % Applied')
    applied_from = fields.Float(string='Applied From')
    applied_to = fields.Float(string='Applied To')

    _sql_constraints = [
        ('unique_tax_slab', 'UNIQUE(name, tax_percent, applied_from, applied_to)', 'The tax slab must be unique!'),
    ]

    @api.constrains('tax_percent')
    def _check_valid_value(self):
        for record in self:
            if record.tax_percent < 1 or record.tax_percent > 100:
                raise ValidationError("Value must be between 1 to 100!")
