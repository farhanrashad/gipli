from odoo import models, fields, api


class TourFacility(models.Model):
    _name = 'tour.facility'
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')
