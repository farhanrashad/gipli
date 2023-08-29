from odoo import models, fields


class TourSeason(models.Model):
    _name = 'tour.season'
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
