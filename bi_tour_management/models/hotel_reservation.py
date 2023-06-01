from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class TourHotelReservation(models.Model):
    _name = 'tour.hotel.reservation'
    _description = 'Tour Hotel Reservation'

    name = fields.Char(string='Registration ID', required=True,
                       readonly=True, default=lambda self: _('New'))
    current_date = fields.Date(string='Date', required=True)
    mobile = fields.Char(string='Mobile', required=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    email = fields.Char(string='Email', related='customer_id.email')
    adult = fields.Integer(string='Adult Person')
    child = fields.Integer(string='Child')
    currency_id = fields.Many2one('res.currency', string='Currency')
    hotel_type_id = fields.Many2one('hotel.type', string='Hotel Type', required=True)
    hotel_id = fields.Many2one('res.partner', string='Hotel', required=True)
    room_type_id = fields.Many2one('product.product', string='Room Type', required=True)
    room_rent = fields.Float(string='Cost Price')
    hotel_rent = fields.Float(string='Sale Price')
    check_in_date = fields.Date(string='Check In Date')
    check_out_date = fields.Date(string='Check Out Date')
    rooms_required = fields.Integer(string='Rooms Required')
    no_of_days = fields.Integer(string='No. of Days', compute='_compute_no_of_days', store=True)
    # tour_id = fields.Many2one('tour.tour', string='Tour')
    # tour_dates_id = fields.Many2one('tour.tour.dates', string='Tour Dates')
    # tour_book_id = fields.Many2one('tour.book', string='Tour Book')
    destination_id = fields.Many2one('tour.destination', string='Destination')

    state = fields.Selection(
        string='Status',
        selection=[('draft', 'Draft'),
                   ('confirm', 'Confirm'),
                   ('approved', 'Approved'),
                   ('booked', 'Booked'),
                   ('issue', 'Ticket Issue'),
                   ('done', 'Done'),
                   ('cancel', 'Cancel'),
                   ],
        required=False, default='draft')

    customer_line_ids = fields.One2many('tour.customer.details', 'hotel_reservation_id', string='Customer Lines')
    tax_id = fields.Many2many('account.tax', string='Taxes')

    untaxed_amount = fields.Float(string='Untaxed Amount', readonly=True)
    tax_amount = fields.Float(string='Taxes', compute='_compute_tax_amount')
    amount_total = fields.Float(string='Customer Invoice Amount', compute='_compute_amount_total')
    hotel_invoice_amount = fields.Float(string='Hotel Invoice Amount', readonly=True)

    invoice_count_total = fields.Integer(string='Invoice', compute='_compute_invoice_count_total')

    @api.depends('check_in_date', 'check_out_date')
    def _compute_no_of_days(self):
        for record in self:
            if record.check_in_date and record.check_out_date:
                delta = record.check_out_date - record.check_in_date
                record.no_of_days = delta.days

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

    # Compute Amount
    def compute_amounts(self):
        for rec in self:
            adult_rec = rec.adult + rec.child
            print(adult_rec)
            rec.untaxed_amount = rec.hotel_rent * adult_rec * rec.no_of_days
            rec.hotel_invoice_amount = rec.room_rent * adult_rec * rec.no_of_days

    # Compute Tax
    @api.depends('tax_id')
    def _compute_tax_amount(self):
        for record in self:
            taxes = record.tax_id.filtered(lambda tax: tax.company_id == self.env.company)
            tax_amount = sum(taxes.mapped('amount'))
            record.tax_amount = tax_amount

    # Compute Total Amount
    @api.depends('untaxed_amount', 'tax_amount')
    def _compute_amount_total(self):
        self.amount_total = 0
        for rec in self:
            rec.amount_total = rec.untaxed_amount + rec.tax_amount

    # Create Invoice When Hotel Is Booked
    def make_booking(self):
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
                'product_id': order.room_type_id.id,
                'name': order.name,
                'quantity': 1,
                'price_unit': order.untaxed_amount,
            }
            self.env['account.move.line'].create(line_vals)

            # Create Invoice For Transporter
            invoice_value = {
                'partner_id': order.hotel_id.id,
                'name': order.name,
                'move_type': 'in_invoice',
                'invoice_date': fields.Date.today(),
            }
            invoice = self.env['account.move'].sudo().create(invoice_value)
            line_value = {
                'move_id': invoice.id,
                'product_id': order.room_type_id.id,
                'name': order.name,
                'quantity': 1,
                'price_unit': order.hotel_invoice_amount,
            }
            self.env['account.move.line'].create(line_value)
            # Mark the sale order as invoiced
            order.write({'state': 'booked'})

    def issue_ticket(self):
        for rec in self:
            rec.state = 'issue'

    def done_hotel(self):
        for rec in self:
            rec.state = 'done'

    def cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'hotel.reservation') or _('New')
        res = super(TourHotelReservation, self).create(vals)
        return res

        # Code For Smart Button

    def _compute_invoice_count_total(self):
        for record in self:
            journal_total = self.env['account.move'].search_count(
                ['|', ('partner_id', '=', record.customer_id.id),
                 ('partner_id', '=', record.hotel_id.id)])
            record.invoice_count_total = journal_total

    def action_hotel_reservation(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'kanban,tree,form',
            'target': 'current',
            'res_model': 'account.move',
            'domain': [('partner_id', '=', self.customer_id.id), ('partner_id', '=', self.hotel_id.id)],
            'context': "{'create': False}",
            'default_move_type': 'out_invoice',
        }

    # End Code For Smart Button