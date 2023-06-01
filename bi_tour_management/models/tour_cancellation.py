from odoo import models, fields


class TourCancellation(models.Model):
    _name = 'tour.cancellation'
    _description = 'Tour Cancellation'

    tour_booking_id = fields.Many2one('tour.booking', string='Tour Booking ID')
    cancel_date = fields.Date(string='TourCancel Date', default=fields.date.today())
    name = fields.Char(string='Tour Cancellation ID')
    current_date = fields.Date(string='Booking Date', related='tour_booking_id.current_date')
    customer_id = fields.Many2one('res.partner', string='Customer', related='tour_booking_id.customer_id')
    email = fields.Char(string='Email', related='tour_booking_id.email')
    mobile = fields.Char(string='Mobile Number', related='tour_booking_id.mobile')
    adult = fields.Integer(string='Adult Persons', related='tour_booking_id.adult')
    child = fields.Integer(string='Child', related='tour_booking_id.child')
    via = fields.Selection([('agent', 'Agent'), ('direct', 'Direct')], string='Via', related='tour_booking_id.via')
    tour_type = fields.Selection([('international', 'International'), ('domestic', 'Domestic')], string='Tour Type',
                                 related='tour_booking_id.tour_type')
    season_id = fields.Many2one('tour.season', string='Season', related='tour_booking_id.season_id')
    tour_id = fields.Many2one('tour.package', string='Tour', related='tour_booking_id.tour_book_id')
    tour_dates_id = fields.Many2one('tour.dates', string='Tour Dates', related='tour_booking_id.tour_dates_id')
    payment_policy_id = fields.Many2one('tour.payment.policy',
                                        string='Payment Policy', related='tour_booking_id.payment_policy_id')
    status = fields.Selection([('draft', 'Draft'), ('in_process', 'In Process'), ('done', 'Done')],
                              string='Status', default='draft')

    def process_record(self):
        for rec in self:
            rec.status = 'in_process'

    def done_cancel(self):
        for rec in self:
            rec.status = 'done'
