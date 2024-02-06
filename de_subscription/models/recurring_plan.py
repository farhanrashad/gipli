# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, _lt, Command
from odoo.tools import get_timedelta


class SubscriptionPlan(models.Model):
    _name = 'sale.recur.plan'
    _description = 'Subscription Plan'

    active = fields.Boolean(default=True)
    name = fields.Char(translate=True, required=True, default="Monthly")
    recurring_interval_type = fields.Selection([
        ('daily', 'Days'), ('weekly', 'Weeks'),
        ('monthly', 'Months'), ('yearly', 'Years'), ],
        string='Recurrence', required=True,
        help="Invoice automatically repeat at specified interval",
        default='monthly')

    recurring_interval = fields.Integer(string="Internal", help="Repeat every (Days/Week/Month/Year)", required=True, default=1)

    company_id = fields.Many2one('res.company')