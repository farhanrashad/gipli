from odoo import models, fields


class TourPackageType(models.Model):
    _name = 'tour.package.type'
    name = fields.Char(string='Package Name', required=True)
    code = fields.Char(string='Package Code', required=True)
