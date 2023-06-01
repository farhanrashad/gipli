from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TransportBooking(models.Model):
    _name = 'transport.booking'

    name = fields.Char(string='Registration ID', required=True,
                       readonly=True, default=lambda self: _('New'))
    mobile = fields.Char(string='Mobile', required=True)
    current_date = fields.Date(string='Booking Date', required=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    email = fields.Char(string='Email', related='customer_id.email')
    adult = fields.Integer(string='Adult', required=True)
    child = fields.Integer(string='Child', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    transport_id = fields.Many2one('transport.information', string='Transport Company', required=True)
    checkin_date = fields.Date(string='Journey Date', required=True)
    transport_carrier_id = fields.Many2one('transport.carrier', string='Carrier Name', required=True)
    transport_type_id = fields.Many2one('product.product', string='Transport Type', required=True)
    travel_class_id = fields.Many2one('travel.class', string='Travel Class', required=True)
    from_destination_id = fields.Many2one('tour.destination', string='From Destination', required=True)
    to_destination_id = fields.Many2one('tour.destination', string='To Destination', required=True)
    # tour_id = fields.Many2one('tour.package', string='Tour')
    # tour_book_id = fields.Many2one('tour.booking', string='Tour Book')
    # tour_date_id = fields.Many2one('tour.dates', string='Tour Date')
    pnr_no = fields.Char(string='PNR No')
    carrier_no = fields.Char(string='Carrier No')
    arrival_date = fields.Date(string='Arrival Date')
    departure_date = fields.Date(string='Departure Date')
    cost_price_adult = fields.Float(string='Cost Price (Adult)')
    cost_price_child = fields.Float(string='Cost Price (Child)')
    sale_price_child = fields.Float(string='Sale Price (Child)')
    sale_price_adult = fields.Float(string='Sale Price (Adult)')
    state = fields.Selection(
        string='Status',
        selection=[('draft', 'Draft'),
                   ('confirm', 'Confirm'),
                   ('approved', 'Approved'),
                   ('invoiced', 'Invoice'),
                   ('issue', 'Ticket Issue'),
                   ('done', 'Done'),
                   ('cancel', 'Cancel'),
                   ],
        required=False, default='draft')

    customer_line_ids = fields.One2many('tour.customer.details', 'transport_booking_id', string='Customer Lines')
    tax_id = fields.Many2many('account.tax', string='Taxes')

    untaxed_amount = fields.Float(string='Untaxed Amount', compute='_compute_untaxed_amount')
    tax_amount = fields.Float(string='Taxes', compute='_compute_tax_amount')
    amount_total = fields.Float(string='Customer Invoice Amount', compute='_compute_amount_total')
    total_amount_transport = fields.Float(string='Transport Invoice Amount', compute='_compute_total_amount_transport')
    invoice_count = fields.Integer(string='Invoice', compute='_compute_invoice_count')

    @api.constrains('arrival_date', 'departure_date')
    def _check_dates(self):
        for record in self:
            if record.arrival_date > record.departure_date:
                raise ValidationError("Arrival date can't be after departure date")

    @api.depends('customer_line_ids')
    def _compute_untaxed_amount(self):
        self.untaxed_amount = 0
        for record in self:
            adult_count = len(self.customer_line_ids.filtered(lambda r: r.adult_child == 'adult'))
            child_count = len(self.customer_line_ids.filtered(lambda r: r.adult_child == 'child'))
            adult_amount_count = record.sale_price_adult * adult_count
            child_amount_count = record.sale_price_child * child_count
            record.untaxed_amount = adult_amount_count + child_amount_count

    @api.depends('tax_id')
    def _compute_tax_amount(self):
        for record in self:
            taxes = record.tax_id.filtered(lambda tax: tax.company_id == self.env.company)
            tax_amount = sum(taxes.mapped('amount'))
            record.tax_amount = tax_amount

    @api.depends('untaxed_amount', 'tax_amount')
    def _compute_amount_total(self):
        self.amount_total = 0
        for rec in self:
            rec.amount_total = rec.untaxed_amount + rec.tax_amount

    @api.depends('untaxed_amount')
    def _compute_total_amount_transport(self):
        self.total_amount_transport = 0
        for record in self:
            adult_count = len(self.customer_line_ids.filtered(lambda r: r.adult_child == 'adult'))
            child_count = len(self.customer_line_ids.filtered(lambda r: r.adult_child == 'child'))
            adult_total_count = record.cost_price_adult * adult_count
            child_total_count = record.cost_price_child * child_count
            record.total_amount_transport = adult_total_count + child_total_count

    def confirm_record(self):
        for record in self:
            adult_rec = record.adult + record.child
            customer_count = len(self.customer_line_ids)
            # Check if the counts match
            if customer_count != adult_rec:
                raise ValidationError(
                    "Customer Record Missing.")
            else:
                record.state = 'confirm'

    def make_approval(self):
        for rec in self:
            rec.state = 'approved'

    def create_invoice(self):
        for order in self:
            invoice_vals = {
                'partner_id': order.customer_id.id,
                'name': order.name,
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.today(),
            }
            invoice = self.env['account.move'].sudo().create(invoice_vals)
            line_vals = {
                'move_id': invoice.id,
                'product_id': order.transport_type_id.id,
                'name': order.name,
                'quantity': 1,
                'price_unit': order.untaxed_amount,
            }
            self.env['account.move.line'].create(line_vals)

            # Create Invoice For Transporter
            invoice_value = {
                'partner_id': order.transport_id.partner_id.id,
                'name': order.name,
                'move_type': 'in_invoice',
                'invoice_date': fields.Date.today(),
            }
            invoice = self.env['account.move'].sudo().create(invoice_value)
            line_value = {
                'move_id': invoice.id,
                'product_id': order.transport_type_id.id,
                'name': order.name,
                'quantity': 1,
                'price_unit': order.total_amount_transport,
            }
            self.env['account.move.line'].create(line_value)
            # Mark the sale order as invoiced
            order.write({'state': 'issue'})

    def booking_done(self):
        for rec in self:
            rec.state = 'done'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'transport.booking') or _('New')
        res = super(TransportBooking, self).create(vals)
        return res

    # Code For Smart Button
    def _compute_invoice_count(self):
        for record in self:
            journal_total = self.env['account.move'].search_count(
                ['|', ('partner_id', '=', record.customer_id.id),
                 ('partner_id', '=', record.transport_id.partner_id.id)])
            record.invoice_count = journal_total

    def action_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'kanban,tree,form',
            'target': 'current',
            'res_model': 'account.move',
            'domain': ['|', ('partner_id', '=', self.customer_id.id),
                       ('partner_id', '=', self.transport_id.partner_id.id)],
            'context': "{'create': False}",
            'default_move_type': 'out_invoice',
        }

    # End Code For Smart Button


class TourCustomerDetails(models.Model):
    _name = 'tour.customer.details'
    _description = 'Tour Customer Details'

    name = fields.Text(string='Age')
    transport_booking_id = fields.Many2one('transport.booking', string='Transport')
    tour_booking_id = fields.Many2one('tour.booking', string='Transport')
    hotel_reservation_id = fields.Many2one('tour.hotel.reservation')
    partner_id = fields.Many2one('res.partner', string='Person')
    gender = fields.Selection(
        string='Gender',
        selection=[('male', 'Male'),
                   ('female', 'Female'), ],
        required=False, default='male')
    adult_child = fields.Selection(
        string='Adult/child',
        selection=[('adult', 'Adult'),
                   ('child', 'Child'), ],
        required=False, default='adult')
    room_no = fields.Char(string='Room No')


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move Inherit'

    def action_post(self):
        res = super(AccountMoveInherit, self).action_post()
        for move in self:
            transport_booking = self.env['transport.booking'].search([('customer_id', '=', move.partner_id.id)])
            if transport_booking:
                transport_booking.write({'state': 'invoiced'})
        return res
