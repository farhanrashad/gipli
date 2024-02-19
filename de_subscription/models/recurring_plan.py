# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, _lt, Command
from odoo.tools import get_timedelta


class SubscriptionPlan(models.Model):
    _name = 'sale.recur.plan'
    _description = 'Subscription Plan'

    active = fields.Boolean(default=True)
    name = fields.Char(translate=True, required=True, default="Monthly")
    recurring_interval_type = fields.Selection([
        ('day', 'Days'), ('week', 'Weeks'),
        ('month', 'Months'), ('year', 'Years'), ],
        string='Recurrence', required=True,
        help="Invoice automatically repeat at specified interval",
        default='month')

    recurring_interval = fields.Integer(string="Interval", help="Repeat every (Days/Week/Month/Year)", required=True, default=1)
    intervals_total = fields.Integer(string="Recurring Intervals", help="No of Recurring Periods", required=True, default=1)

    company_id = fields.Many2one('res.company')

    @property
    def billing_period(self):
        if not self.recurring_interval_type or not self.recurring_interval:
            return False
        return get_timedelta(self.recurring_interval, self.recurring_interval_type)