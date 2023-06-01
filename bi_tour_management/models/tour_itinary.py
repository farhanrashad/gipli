from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class CustomTourItinerary(models.Model):
    _name = 'custom.tour.itinerary'

    tour_preference_id = fields.Many2one('tour.preference', string='Customer Inquiry', required=True)
    lead_id = fields.Many2one('crm.lead', string='Lead', required=True)
    name = fields.Char(string='Tour Name', required=True)
    product_itinerary_id = fields.Many2one('product.product', string='Tour', required=True)
    address = fields.Char(string='Address')
    mobile = fields.Char(string='Mobile', required=True)
    email = fields.Char(string='Email', required=True)
    contact = fields.Char(string='Contact')
    via = fields.Selection([('direct', 'Direct'), ('agent', 'Agent')], string='Via', required=True)
    check_in_date = fields.Date(string='Prefer Start Date', required=True)
    check_out_date = fields.Date(string='Prefer End Date')
    tour_payment_policy_id = fields.Many2one('tour.payment.policy', string='Payment Policy')
    adult = fields.Integer(string='Adult', required=True)
    season_id = fields.Many2one('tour.season', string='Season', required=True)
    child = fields.Integer(string='Child', required=True)
    room_required = fields.Integer(string='Room Required')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    due_date = fields.Date(string='Payment Due Date', required=True)
    book_date = fields.Date(string='Last Date of Booking', required=True)
    total_seats = fields.Integer(string='Total Seats', compute='_compute_total_seats')
    tour_program_ids = fields.One2many('tour.program', 'tour_itinerary_id', string='Tour Programs')
    tour_book_destination_ids = fields.One2many('tour.destination.line', 'tour_itinerary_id',
                                                string='Tour Destinations')
    tour_cost_include_facility_ids = fields.One2many('tour.cost.include.facility', 'tour_itinerary_id',
                                                     string='Cost Include')
    tour_cost_exclude_facility_ids = fields.One2many('tour.cost.exclude.facility', 'tour_itinerary_id',
                                                     string='Cost Exclude')
    sites_cost_book_ids = fields.One2many('sites.costing.line', 'tour_itinerary_id',
                                          string='Site Cost')
    visa_cost_ids = fields.One2many('visa.costing.line', 'tour_booking_id',
                                    string='Visa Cost')
    hotel_planner_book_ids = fields.One2many('hotel.planner.detail', 'tour_itinerary_id',
                                             string='Hotel Details')
    travel_planner_book_ids = fields.One2many('travel.planner.details', 'tour_itinerary_id',
                                              string='Travel Planner')
    tour_services_book_ids = fields.One2many('tour.service.line.details', 'tour_itinerary_id',
                                             string='Other Services')
    sub_total = fields.Float(string='Total UnTaxed Amount', compute='_compute_sub_total')
    tax_amount = fields.Float(string='Total Taxe Amount', compute='_compute_tax_amount')
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount')
    # quotation_count = fields.Integer(string='Invoice', compute='_compute_quotation_count')

    state = fields.Selection(
        string='Status',
        selection=[('draft', 'Draft'),
                   ('confirm', 'Confirm'),
                   ('approved', 'Approved'),
                   ('done', 'Done'),
                   ('refuse', 'Refuse'),
                   ],
        required=False, default='draft')

    @api.constrains('due_date', 'book_date')
    def _check_dates(self):
        for record in self:
            if record.book_date and record.start_date:
                if record.book_date < record.due_date:
                    raise ValidationError("Due Date Must be Small than start date.")

    @api.constrains('book_date', 'start_date')
    def _check_dates(self):
        for record in self:
            if record.book_date and record.start_date:
                if record.book_date > record.start_date:
                    raise ValidationError("Last Date of Booking be Smaller than start date.")

    @api.depends('adult', 'child')
    def _compute_total_seats(self):
        for rec in self:
            rec.total_seats = rec.adult + rec.child

    def _compute_sub_total(self):
        for order in self:
            program_total = sum(order.tour_program_ids.mapped('total_sale_price'))
            site_cost_total = sum(order.sites_cost_book_ids.mapped('total_sale_price'))
            visa_cost_total = sum(order.visa_cost_ids.mapped('total_price'))
            customer_price_total = sum(order.hotel_planner_book_ids.mapped('total_customer_price'))
            travel_price_total = sum(order.travel_planner_book_ids.mapped('total_sale_price_adult')) + sum(
                order.travel_planner_book_ids.mapped('total_sale_price_child'))
            other_services_total = sum(order.tour_services_book_ids.mapped('price_subtotal'))
            order.sub_total = program_total + site_cost_total + customer_price_total + visa_cost_total + travel_price_total + other_services_total

    @api.depends('visa_cost_ids.sale_tax_amount_visa', 'hotel_planner_book_ids.sale_tax_amount_htl')
    def _compute_tax_amount(self):
        for record in self:
            visa_tax_total = sum(record.visa_cost_ids.mapped('sale_tax_amount_visa'))
            hotel_tax_total = sum(record.hotel_planner_book_ids.mapped('sale_tax_amount_htl'))
            travel_tax_total = sum(record.travel_planner_book_ids.mapped('sale_tax_amount_trvl'))
            other_services_tax_total = sum(record.tour_services_book_ids.mapped('sale_tax_amount_tour'))
            record.tax_amount = visa_tax_total + hotel_tax_total + travel_tax_total + other_services_tax_total

    @api.depends('visa_cost_ids')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.sub_total + record.tax_amount

    def confirm_record(self):
        for record in self:
            record.state = 'confirm'

    def make_approval_tour(self):
        for rec in self:
            rec.state = 'approved'

    def create_tour(self):
        for rec in self:
            rec.state = 'done'

    def cancel(self):
        for rec in self:
            rec.state = 'refuse'