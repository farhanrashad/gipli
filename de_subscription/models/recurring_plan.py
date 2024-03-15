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

    upsell_portal_product_ids = fields.Many2many(
        'product.product',
        'upsell_product_rel',
        'product_id',
        'upsell_id',
        string='Upsell Products',
        domain=[('is_recurring', '=', True)],
    )
    recurring_interval_display = fields.Char('Recurring Interval', 
                                           compute='_compute_all_recurring')
    recurring_period_display = fields.Char('Recurring Period', 
                                           compute='_compute_all_recurring')
    

    def _compute_all_recurring(self):
        interval_type = total_interval_type = ''
        for plan in self:
            if plan.recurring_interval > 1:
                interval_type = plan.recurring_interval_type + 's'
            else:
                interval_type = plan.recurring_interval_type
            if plan.intervals_total > 1:
                total_interval_type = plan.recurring_interval_type + 's'
            else:
                total_interval_type = plan.recurring_interval_type
            
            plan.recurring_interval_display = str(plan.recurring_interval) + ' ' + interval_type.capitalize()
            plan.recurring_period_display = str(plan.intervals_total) + ' ' + total_interval_type.capitalize()
    @property
    def billing_period(self):
        if not self.recurring_interval_type or not self.recurring_interval:
            return False
        return get_timedelta(self.recurring_interval, self.recurring_interval_type)