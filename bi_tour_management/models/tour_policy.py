from odoo import models, fields


class TourPaymentPolicy(models.Model):
    _name = 'tour.payment.policy'
    _description = 'Tour Payment Policy'

    name = fields.Char(required=True)
    before_book_date_per = fields.Integer(string='Payment Percentage Before Booking Date')
    before_pay_date_per = fields.Integer(string='Payment Percentage After Booking Date')
