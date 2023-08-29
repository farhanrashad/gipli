from odoo import models, fields


class TourPackage(models.Model):
    _name = 'tour.package'
    _description = 'Tour Package'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    product_id = fields.Many2one('product.product', string='Tour Name', required=True)
    tour_type = fields.Selection([('international', 'International'), ('domestic', 'Domestic')],
                                 string='Tour Type', required=True)
    current_date = fields.Date(string='Date Of Publish')
    days = fields.Integer(string='Days', required=True)
    tour_road_travel_lines_id = fields.One2many('tour.road.travel', 'tour_package_id', string='Travel Information')
    tour_date_lines = fields.One2many('tour.dates', 'tour_id', string='Tour Dates')
    tour_program_book_ids = fields.One2many('tour.program', 'tour_package_id', string='Tour Programs')
    tour_book_destination_ids = fields.One2many('tour.destination.line', 'tour_package_id', string='Tour Destinations')
    tour_cost_include_facility_ids = fields.One2many('tour.cost.include.facility', 'tour_package_id',
                                                     string='Cost Include')
    tour_cost_exclude_facility_ids = fields.One2many('tour.cost.exclude.facility', 'tour_package_id',
                                                     string='Cost Exclude')
    sites_cost_book_ids = fields.One2many('sites.costing.line', 'tour_package_id',
                                          string='Site Cost')
    visa_cost_ids = fields.One2many('visa.costing.line', 'tour_package_id',
                                    string='Visa Cost')
    hotel_planner_book_ids = fields.One2many('hotel.planner.detail', 'tour_package_id',
                                             string='Hotel Details')
    travel_planner_book_ids = fields.One2many('travel.planner.details', 'tour_package_id',
                                              string='Travel Planner')
    tour_services_book_ids = fields.One2many('tour.service.line.details', 'tour_package_id',
                                             string='Other Services')
    state = fields.Selection(
        string='Status',
        selection=[('draft', 'Draft'),
                   ('confirm', 'Confirm'),
                   ],
        required=False, default='draft')

    def confirm_record(self):
        for record in self:
            record.state = 'confirm'


class TourRoadTravel(models.Model):
    _name = 'tour.road.travel'
    _description = 'Road Travel Tour'

    from_destination_id = fields.Many2one('tour.destination', string='From')
    to_destination_id = fields.Many2one('tour.destination', string='To')
    transport_type_id = fields.Many2one('product.product', string='Transport Type')
    travel_class_id = fields.Many2one('travel.class', string='Travel Class')
    name = fields.Char(string='Distance In KM')
    approx_time = fields.Float(string='Time(Hrs)')
    provider_ids = fields.One2many('tour.provider', 'tour_id', string='Providers Information')
    tour_package_id = fields.Many2one('tour.package')


class TourProvider(models.Model):
    _name = 'tour.provider'

    name = fields.Boolean(string='Primary')
    tour_id = fields.Many2one('tour.road.travel', string='Tour')
    provider_id = fields.Many2one('transport.information', 'Service Provider')
    transport_carrier_id = fields.Many2one('transport.carrier', 'Service Provider')


class TourDates(models.Model):
    _name = 'tour.dates'
    _description = 'Tour Dates'
    _rec_name = 'start_date'

    season_id = fields.Many2one('tour.season', string='Season')
    start_date = fields.Date(string='Start Date')
    book_date = fields.Date(string='Book Date')
    due_date = fields.Date(string='Due Date')
    total_seats = fields.Integer(string='Total Seats')
    available_seats = fields.Integer(string='Available Seats')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('close', 'Close'),
        ('reopen', 'Reopen'),
    ], string='Status', default='draft')
    tour_id = fields.Many2one('tour.package', string='Tour')
