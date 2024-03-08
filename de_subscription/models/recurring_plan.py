# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, _lt, Command
from odoo.tools import get_timedelta


class SubscriptionPlan(models.Model):
    _name = 'sale.recur.plan'
    _description = 'Subscription Plan'

    active = fields.Boolean(default=True)
    name = fields.Char(translate=True, required=True, default="Monthly")
    description = fields.Html('About Recurring Plan', translate=True)
    recurring_interval_type = fields.Selection([
        ('day', 'Days'), ('week', 'Weeks'),
        ('month', 'Months'), ('year', 'Years'), ],
        string='Recurrence', required=True,
        help="Invoice automatically repeat at specified interval",
        default='month')

    recurring_interval = fields.Integer(string="Interval", help="Repeat every (Days/Week/Month/Year)", required=True, default=1)
    intervals_total = fields.Integer(string="Recurring Intervals", help="No of Recurring Periods", required=True, default=1)

    invoice_mail_template_id = fields.Many2one('mail.template', string='Invoice Email Template',
                                               domain=[('model', '=', 'account.move')],
                                               default=lambda self: self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False),
                                               help="Email template used to send invoicing email automatically.\n"
                                                    "Leave it empty if you don't want to send email automatically.")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    allow_portal_closing = fields.Boolean('Closure by Customers')

    allow_portal_upsell = fields.Boolean('Upsell by Customers')
    allow_portal_renewal = fields.Boolean('Renewal by Customers')


    @property
    def billing_period(self):
        if not self.recurring_interval_type or not self.recurring_interval:
            return False
        return get_timedelta(self.recurring_interval, self.recurring_interval_type)