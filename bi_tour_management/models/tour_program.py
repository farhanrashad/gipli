from odoo import models, api, fields


class TourProgram(models.Model):
    _name = 'tour.program'
    _description = 'Tour Program'
    _rec_name = 'tour_code'

    tour_code = fields.Char(string='Tour Code', required=True)
    days = fields.Integer(string='Days', required=True)
    description = fields.Text(string='Description', required=True)
    break_fast = fields.Boolean(string='Breakfast')
    lunch = fields.Boolean(string='Lunch')
    dinner = fields.Boolean(string='Dinner')
    sale_price = fields.Float(string='Sale Price')
    total_sale_price = fields.Float('Total Sale Price', compute='_compute_total_sale_price')

    # product_ids = fields.Many2many('product.product', string='Products')
    tour_booking_id = fields.Many2one('tour.booking')
    tour_itinerary_id = fields.Many2one('custom.tour.itinerary')
    tour_package_id = fields.Many2one('tour.package')

    @api.depends('sale_price', 'days')
    def _compute_total_sale_price(self):
        for order in self:
            order.total_sale_price = order.sale_price * order.days
