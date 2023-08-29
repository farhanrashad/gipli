from odoo import fields, models


class TourPreference(models.Model):
    _name = 'tour.preference'
    _description = 'Tour Preference'
    _rec_name = 'contact_name'

    current_date = fields.Date(string='Inquiry Date')
    email = fields.Char(string='Email')
    adult = fields.Integer(string='Adult Persons')
    child = fields.Integer(string='Child')
    lead_id = fields.Many2one('crm.lead', string='Lead')
    mobile = fields.Char(string='Mobile', required=True)
    address = fields.Text(string='Address')
    contact_name = fields.Char(string='Contact Name')
    check_in_date = fields.Date(string='Prefer Start Date', required=True)
    check_out_date = fields.Date(string='Prefer End Date', required=True)
    tour_low_price = fields.Float(string='Budget Person (Min)')
    tour_high_price = fields.Float(string='Budget Person (Max)')
    destination_line_ids = fields.One2many('custom.tour.destination', 'preference_id', string='Destination Lines')
    transport_ids = fields.One2many('custom.tour.transport', 'preference_id', string='Transport Preferences')
    hotel_type_id = fields.Many2one('hotel.type', string='Hotel Type')
    room_type_id = fields.Many2one('product.product', string='Room Type')
    room_req = fields.Integer(string='No of Room Required')
    low_price = fields.Integer(string='Price Limit (Min)')
    high_price = fields.Integer(string='Price Limit (Max)')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
    ], string='State', default='draft')
    via = fields.Selection([
        ('direct', 'Direct'),
        ('agent', 'Agent'),
    ], string='Via', default='direct')

    def confirm_tour_record(self):
        for rec in self:
            rec.state = 'confirm'


class CustomTourDestination(models.Model):
    _name = 'custom.tour.destination'
    _description = 'Custom Tour Destination'

    name = fields.Char(string='No. Of Nights', required=True)
    destination_id = fields.Char(string='Destination ID')
    country_id = fields.Many2one('res.country', string='Country')
    preference_id = fields.Many2one('tour.preference')
    site_lines_ids = fields.One2many('custom.tour.destination.site.line', 'custom_destination_id', string='Site Lines')


class CustomTourDestinationSiteLine(models.Model):
    _name = 'custom.tour.destination.site.line'
    _description = 'Custom Tour Destination Site Line'

    name = fields.Char(string='Name', required=True)
    custom_destination_id = fields.Many2one('custom.tour.destination', string='Destination')


class TransportPreference(models.Model):
    _name = 'custom.tour.transport'
    _description = 'Transport Preference'

    name = fields.Selection([
        ('destination', 'Between Destinations'),
        ('site', 'Site Seeing'),
    ], string='Name', default='direct')
    product_id = fields.Many2one('product.product', string='Product Type')
    travel_class_id = fields.Many2one('travel.class', string='Travel Class')
    preference_id = fields.Many2one('tour.preference')
