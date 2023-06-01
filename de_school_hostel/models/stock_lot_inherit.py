from odoo import models, fields, api


class StockProductionLot(models.Model):
    _inherit = 'stock.lot'

    hostel_room = fields.Boolean(string='Hostel Room', store=True, required=True, default=True)
    hostel_id = fields.Many2one('oe.school.hostel', string='Hostel')


