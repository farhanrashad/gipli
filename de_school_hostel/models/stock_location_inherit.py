from odoo import models, fields, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_hostel_room = fields.Boolean(string='Is Hostel Room')
