from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class TourBooking(models.Model):
    _name = 'tour.booking'
    _description = 'Tour Booking'

    name = fields.Char(string='Registration ID', required=True,
                       readonly=True, default=lambda self: _('New'))
    current_date = fields.Date(string='Date', required=True)
    mobile = fields.Char(string='Mobile', required=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    email = fields.Char(string='Email', related='customer_id.email')
    adult = fields.Integer(string='Adult Person')
    child = fields.Integer(string='Child')
    via = fields.Selection(
        string='Via',
        selection=[('direct', 'Direct'),
                   ('agent', 'Agent'), ],
        required=True, default='direct')
    currency_id = fields.Many2one('res.currency', string='Currency')
    tour_type = fields.Selection(
        string='Tour Type',
        selection=[('international', 'International'),
                   ('domestic', 'Domestic'), ],
        required=True, default='domestic')
    season_id = fields.Many2one('tour.season', string='Season')
    payment_policy_id = fields.Many2one('tour.payment.policy')
    tour_id = fields.Many2one('product.product', string='Tour')
    tour_dates_id = fields.Many2one('tour.dates', string='Tour Dates')
    tour_book_id = fields.Many2one('tour.package', string='Tour')

    state = fields.Selection(
        string='Status',
        selection=[('draft', 'Draft'),
                   ('confirm', 'Confirm'),
                   ('in_progress', 'In Progress'),
                   ('booked', 'Booked'),
                   ('invoiced', 'Invoiced'),
                   ('done', 'Done'),
                   ('cancel', 'Cancel'),
                   ],
        required=False, default='draft')

    tour_customer_ids = fields.One2many('tour.customer.details', 'tour_booking_id', string='Customer Lines')
    tour_program_book_ids = fields.One2many('tour.program', 'tour_booking_id', string='Tour Programs')
    tour_book_destination_ids = fields.One2many('tour.destination.line', 'tour_booking_id', string='Tour Destinations')
    tour_cost_include_facility_ids = fields.One2many('tour.cost.include.facility', 'tour_booking_id',
                                                     string='Cost Include')
    tour_cost_exclude_facility_ids = fields.One2many('tour.cost.exclude.facility', 'tour_booking_id',
                                                     string='Cost Exclude')
    sites_cost_book_ids = fields.One2many('sites.costing.line', 'tour_booking_id',
                                          string='Site Cost')
    visa_cost_ids = fields.One2many('visa.costing.line', 'tour_booking_id',
                                    string='Visa Cost')
    hotel_planner_book_ids = fields.One2many('hotel.planner.detail', 'tour_booking_id',
                                             string='Hotel Details')
    travel_planner_book_ids = fields.One2many('travel.planner.details', 'tour_booking_id',
                                              string='Travel Planner')
    tour_services_book_ids = fields.One2many('tour.service.line.details', 'tour_booking_id',
                                             string='Other Services')
    insurance_policy_ids = fields.One2many('insurance.policy', 'tour_booking_id',
                                           string='Services')

    sub_total = fields.Float(string='Sub Total', compute='_compute_sub_total')
    tax_amount = fields.Float(string='Total Taxe Amount', compute='_compute_tax_amount')
    total_insurance_amount = fields.Float(string='Total Insurance Amount', compute='_compute_total_insurance_amount')
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount')
    quotation_count = fields.Integer(string='Invoice', compute='_compute_quotation_count')

    @api.depends('visa_cost_ids.sale_tax_amount_visa', 'hotel_planner_book_ids.sale_tax_amount_htl')
    def _compute_tax_amount(self):
        for record in self:
            visa_tax_total = sum(record.visa_cost_ids.mapped('sale_tax_amount_visa'))
            hotel_tax_total = sum(record.hotel_planner_book_ids.mapped('sale_tax_amount_htl'))
            travel_tax_total = sum(record.travel_planner_book_ids.mapped('sale_tax_amount_trvl'))
            other_services_tax_total = sum(record.tour_services_book_ids.mapped('sale_tax_amount_tour'))
            record.tax_amount = visa_tax_total + hotel_tax_total + travel_tax_total + other_services_tax_total

    @api.depends('insurance_policy_ids.total_cost')
    def _compute_total_insurance_amount(self):
        for record in self:
            services_total = sum(record.insurance_policy_ids.mapped('total_cost'))
            record.total_insurance_amount = services_total

    @api.depends('tour_program_book_ids.total_sale_price', 'sites_cost_book_ids.total_sale_price',
                 'visa_cost_ids.total_price',
                 'hotel_planner_book_ids.total_customer_price')
    def _compute_sub_total(self):
        for order in self:
            program_total = sum(order.tour_program_book_ids.mapped('total_sale_price'))
            site_cost_total = sum(order.sites_cost_book_ids.mapped('total_sale_price'))
            visa_cost_total = sum(order.visa_cost_ids.mapped('total_price'))
            customer_price_total = sum(order.hotel_planner_book_ids.mapped('total_customer_price'))
            travel_price_total = sum(order.travel_planner_book_ids.mapped('total_sale_price_adult')) + sum(
                order.travel_planner_book_ids.mapped('total_sale_price_child'))
            other_services_total = sum(order.tour_services_book_ids.mapped('price_subtotal'))
            order.sub_total = program_total + site_cost_total + customer_price_total + visa_cost_total + travel_price_total + other_services_total

    @api.depends('visa_cost_ids')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.sub_total + record.tax_amount + record.total_insurance_amount

    def confirm_record(self):
        for record in self:
            adult_rec = record.adult + record.child
            customer_count = len(self.tour_customer_ids)
            # Check if the counts match
            if customer_count != adult_rec:
                raise ValidationError(
                    "Customer Record Missing.")
            else:
                record.state = 'confirm'

    def make_approval_tour(self):
        for rec in self:
            rec.state = 'in_progress'

    # # Create Invoice When Hotel Is Booked
    def make_booking(self):
        for order in self:
            invoice_vals = {
                'partner_id': order.customer_id.id,
                'tour_book': order.name,
                'date_order': fields.Date.today(),
                'state': 'sale',
            }
            sale_order_line = self.env['sale.order'].sudo().create(invoice_vals)
            line_vals = {
                'order_id': sale_order_line.id,
                'product_id': order.tour_id.id,
                'product_uom_qty': 1,
                'price_unit': order.total_amount,
            }
            self.env['sale.order.line'].create(line_vals)
            order.write({'state': 'booked'})

    def done_tour(self):
        for rec in self:
            rec.state = 'done'

    def cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'tour.booking') or _('New')
        res = super(TourBooking, self).create(vals)
        return res

    #     # Code For Smart Button
    def _compute_quotation_count(self):
        for record in self:
            quotation_total = self.env['sale.order'].search_count(
                [('partner_id', '=', record.customer_id.id)])
            record.quotation_count = quotation_total

    def action_tour_booking(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quotation',
            'view_mode': 'kanban,tree,form',
            'target': 'current',
            'res_model': 'sale.order',
            'domain': [('partner_id', '=', self.customer_id.id)],
            'context': "{'create': False}",
        }
    #
    # End Code For Smart Button


class TourDestinationLines(models.Model):
    _name = 'tour.destination.line'
    _description = 'Tour Destination Lines'

    destination_id = fields.Many2one('tour.destination', string='Destinations', required=True)
    country_id = fields.Many2one('res.country', string='Country', required=True)
    night = fields.Char(string='No of Nights')
    is_visa = fields.Boolean(string='Is Visa Required')
    tour_booking_id = fields.Many2one('tour.booking')
    tour_itinerary_id = fields.Many2one('custom.tour.itinerary')
    tour_package_id = fields.Many2one('tour.package')


class CostInclude(models.Model):
    _name = 'tour.cost.include.facility'
    _description = 'Cost Include Facility'

    tour_facility_id = fields.Many2one('tour.facility')
    name = fields.Text(string='Description', related='tour_facility_id.description')
    tour_booking_id = fields.Many2one('tour.booking')
    tour_itinerary_id = fields.Many2one('custom.tour.itinerary')
    tour_package_id = fields.Many2one('tour.package')


class CostExclude(models.Model):
    _name = 'tour.cost.exclude.facility'
    _description = 'Cost Exclude Facility'

    tour_facility_id = fields.Many2one('tour.facility')
    name = fields.Text(string='Description', related='tour_facility_id.description')
    tour_booking_id = fields.Many2one('tour.booking')
    tour_itinerary_id = fields.Many2one('custom.tour.itinerary')
    tour_package_id = fields.Many2one('tour.package')


class SiteCost(models.Model):
    _name = 'sites.costing.line'
    _description = 'Site Costing Line'

    product_id = fields.Many2one('product.product', string='Sites Name')
    new_sale_price = fields.Char(string='Sale Price/Person')
    total_sale_price = fields.Float(string='Total Sale Price')
    tour_booking_id = fields.Many2one('tour.booking')
    tour_itinerary_id = fields.Many2one('custom.tour.itinerary')
    tour_package_id = fields.Many2one('tour.package')


class VisaCostingLine(models.Model):
    _name = 'visa.costing.line'

    name = fields.Char(string="Visa", required=True)
    country_id = fields.Many2one('res.country', string="Country", required=True)
    visa_type = fields.Selection(
        [('tourist_visa_single_entry', 'Tourist Visa Single Entry'),
         ('tourist_visa_double_entry', 'Tourist Visa Double Entry')],
        string="Visa Type", default='tourist_visa_single_entry')
    sale_price = fields.Float(string="Visa Sale Price")
    sale_tax_ids = fields.Many2many('account.tax', string="Sales Taxes")
    total_person = fields.Integer(string="No. of Person", required=True)
    total_price = fields.Float(string="Total Sale Price", compute="_compute_total_price")
    sale_tax_amount_visa = fields.Float(string="Sale Tax Amount Visa", compute='_compute_sale_tax_amount_visa')
    visa_pin_sale = fields.Float(string="Sale Amount", compute='_compute_visa_pin_sale')
    tour_booking_id = fields.Many2one('tour.booking')
    tour_itinerary_id = fields.Many2one('custom.tour.itinerary')
    tour_package_id = fields.Many2one('tour.package')

    @api.depends('sale_price', 'sale_tax_ids', 'total_person')
    def _compute_total_price(self):
        self.total_price = 0
        for rec in self:
            rec.total_price = rec.total_person * rec.sale_price

    @api.depends('sale_tax_ids')
    def _compute_sale_tax_amount_visa(self):
        for record in self:
            taxes = record.sale_tax_ids.filtered(lambda tax: tax.company_id == self.env.company)
            tax_amount = sum(taxes.mapped('amount'))
            record.sale_tax_amount_visa = tax_amount * record.total_person

    @api.depends('sale_tax_ids', 'total_price')
    def _compute_visa_pin_sale(self):
        for rec in self:
            rec.visa_pin_sale = rec.total_price + rec.sale_tax_amount_visa


class HotelPlannerDetail(models.Model):
    _name = 'hotel.planner.detail'

    name = fields.Char(string='Sequence', required=True)
    destination_id = fields.Many2one('tour.destination', string='Destination', required=True)
    hotel_id = fields.Many2one('res.partner', string='Hotel', required=True)
    hotel_type_id = fields.Many2one('hotel.type', string='Hotel Type', required=True)
    room_type_id = fields.Many2one('product.product', string='Room Type', required=True)
    room_required = fields.Integer(string='Rooms Required')
    days = fields.Integer(string='No. of Days To Stay')
    customer_price = fields.Float(string='Customer Rent / Night')
    total_customer_price = fields.Float(string='Total Customer Price', compute="_compute_total_customer_price")
    pur_bol = fields.Boolean(string='Show Purchase Tax')
    sale_tax_ids = fields.Many2many('account.tax', string='Sale Taxes')
    sale_tax_amount_htl = fields.Float(string="Sale Tax Amount", compute='_compute_sale_tax_amount_htl')
    hotel_pln_sale = fields.Float(string="Sale Amount", compute='_compute_hotel_pln_sale')
    tour_booking_id = fields.Many2one('tour.booking')
    tour_itinerary_id = fields.Many2one('custom.tour.itinerary')
    tour_package_id = fields.Many2one('tour.package')

    @api.depends('days', 'customer_price')
    def _compute_total_customer_price(self):
        self.total_customer_price = 0
        for rec in self:
            rec.total_customer_price = rec.days * rec.customer_price

    @api.depends('sale_tax_ids')
    def _compute_sale_tax_amount_htl(self):
        for record in self:
            taxes = record.sale_tax_ids.filtered(lambda tax: tax.company_id == self.env.company)
            tax_amount = sum(taxes.mapped('amount'))
            record.sale_tax_amount_htl = tax_amount * record.days

    @api.depends('sale_tax_amount_htl', 'total_customer_price')
    def _compute_hotel_pln_sale(self):
        for rec in self:
            rec.hotel_pln_sale = rec.total_customer_price + rec.sale_tax_amount_htl


# Travel Details
class TravelPlannerDetails(models.Model):
    _name = 'travel.planner.details'
    _description = 'Travel Planner Details'

    name = fields.Char(string='Name')
    transport_id = fields.Many2one('transport.information', string='Transport Company')
    date = fields.Date(string='Booking Date')
    transport_carrier_id = fields.Many2one('transport.carrier', string='Carrier Name')
    transport_type_id = fields.Many2one('product.product', string='Transport Type')
    travel_class_id = fields.Many2one('travel.class', string='Travel Class')
    from_dest_id = fields.Many2one('tour.destination', string='From')
    to_dest_id = fields.Many2one('tour.destination', string='To')
    sale_price_adult = fields.Float(string='Sale Price (Adult)')
    sale_price_child = fields.Float(string='Sale Price (Child)')
    total_sale_price_adult = fields.Float(string='Total Sale Price (Adult)', compute='_compute_total_sale_price_adult')
    total_sale_price_child = fields.Float(string='Total Sale Price (Child)', compute='_compute_total_sale_price_child')
    pur_bol = fields.Boolean(string='Show Purchase Tax')
    sale_tax_ids = fields.Many2many('account.tax', string='Sale Taxes')
    sale_tax_amount_trvl = fields.Float(string="Sale Tax Amount", compute='_compute_sale_tax_amount_trvl')
    travel_pln_sale = fields.Float(string="Sale Amount", compute='_compute_travel_pln_sale')
    tour_booking_id = fields.Many2one('tour.booking', 'Tour Booking')
    tour_itinerary_id = fields.Many2one('custom.tour.itinerary')
    tour_package_id = fields.Many2one('tour.package')

    @api.depends('sale_tax_ids')
    def _compute_sale_tax_amount_trvl(self):
        for record in self:
            total_per = self.tour_booking_id.adult + self.tour_booking_id.child
            taxes = record.sale_tax_ids.filtered(lambda tax: tax.company_id == self.env.company)
            tax_amount = sum(taxes.mapped('amount'))
            record.sale_tax_amount_trvl = tax_amount * total_per

    @api.depends('sale_tax_amount_trvl', 'total_sale_price_adult', 'total_sale_price_child')
    def _compute_travel_pln_sale(self):
        for rec in self:
            rec.travel_pln_sale = rec.total_sale_price_adult + rec.total_sale_price_child + rec.sale_tax_amount_trvl

    @api.depends('tour_booking_id.adult', 'sale_price_adult')
    def _compute_total_sale_price_adult(self):
        for detail in self:
            detail.total_sale_price_adult = detail.tour_booking_id.adult * detail.sale_price_adult

    @api.depends('tour_booking_id.child', 'sale_price_child')
    def _compute_total_sale_price_child(self):
        for detail in self:
            detail.total_sale_price_child = detail.tour_booking_id.child * detail.sale_price_child


class TourServiceLineDetails(models.Model):
    _name = 'tour.service.line.details'
    _description = 'Tour Service Line Details'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    sale_price = fields.Float(string='Sale Price', required=True, related='product_id.lst_price')
    product_uom_qty = fields.Float(string='Quantity(UOM)', required=True, default=1)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True, related='product_id.uom_id')
    discount = fields.Float(string='Discount')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_price_subtotal')
    pur_bol = fields.Boolean(string='Show Purchase Tax')
    sale_tax_ids = fields.Many2many('account.tax', string='Sale Taxes')
    sale_tax_amount_tour = fields.Float(string="Sale Tax Amount", compute='_compute_sale_tax_amount_tour')
    sale_tour_services = fields.Float(string="Sale Amount", compute='_compute_sale_tour_services')
    tour_booking_id = fields.Many2one('tour.booking', 'Tour Booking')
    tour_itinerary_id = fields.Many2one('custom.tour.itinerary')
    tour_package_id = fields.Many2one('tour.package')

    @api.depends('product_uom_qty', 'sale_price')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.sale_price * rec.product_uom_qty

    @api.depends('sale_tax_ids')
    def _compute_sale_tax_amount_tour(self):
        for record in self:
            taxes = record.sale_tax_ids.filtered(lambda tax: tax.company_id == self.env.company)
            tax_amount = sum(taxes.mapped('amount'))
            record.sale_tax_amount_tour = tax_amount * record.product_uom_qty

    @api.depends('sale_tax_amount_tour', 'price_subtotal')
    def _compute_sale_tour_services(self):
        for rec in self:
            rec.sale_tour_services = rec.price_subtotal + rec.sale_tax_amount_tour - rec.discount
