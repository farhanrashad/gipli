from odoo import models, fields


class TourDestination(models.Model):
    _name = 'tour.destination'
    _description = 'Tour Destination'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    country_id = fields.Many2one('res.country', string='Country', required=True)
