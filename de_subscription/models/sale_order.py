# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, date
from odoo import api, fields, models, _
from odoo.tools import float_compare, format_datetime, format_time
from pytz import timezone, UTC


class SubscriptionOrder(models.Model):
    _inherit = 'sale.order'

    SUB_READONLY_STATES = {
        'progress': [('readonly', True)],
        'close': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    def _get_default_subscription_plan(self):
        plan_id = self.env['sale.recur.plan'].search([('active','=',True)],limit=1)
        return plan_id

    
    subscription_order = fields.Boolean("Subscription")
    subscription_status = fields.Selection([
        ('draft', 'Quotation'),  # Quotation for a new subscription
        ('progress', 'In Progress'),  # Active Subscription or confirmed renewal for active subscription
        ('close', 'Close'),  # Closed or ended subscription
    ], 
        string='Subscription Status', compute='_compute_subscription_status', store=True, index='btree_not_null', tracking=True, group_expand='_group_expand_states',
    )

    subscription_plan_id = fields.Many2one('sale.recur.plan', string='Recurring Plan',
                            default=lambda s: s._get_default_subscription_plan(),
                              ondelete='restrict', readonly=False, store=True, index='btree_not_null')

    date_last_invoice = fields.Date(string='Last invoice date', compute='_compute_last_invoice_date')
    date_next_invoice = fields.Date(
        string='Date of Next Invoice',
        compute='_compute_next_invoice_date',
        store=True, copy=False,
        readonly=False,
        tracking=True,
        help="The next invoice will be created on this date then the period will be extended.")
    date_start = fields.Date(string='Start Date',
                             compute='_compute_start_date',
                             readonly=False,
                             store=True,
                             tracking=True,
                             help="The start date indicate when the subscription periods begin.")
    
    date_end = fields.Date(string='End Date', tracking=True,
                           help="If set in advance, the subscription will be set to renew 1 month before the date and will be closed on the date set in this field.")
    date_first_contract = fields.Date(
        compute='_compute_contact_start_date',
        store=True,
        help="The first contract date is the start date of the first contract of the sequence. It is common across a subscription and its renewals.")
    
    # =======================================================================
    # ========================== Computed Mehtods ===========================
    # =======================================================================
    
    @api.depends('subscription_order')
    def _compute_subscription_status(self):
        
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            #elif order.subscription_status in ['2_renewal', '7_upsell']:
            #    continue
            elif order.subscription_order or order.state == 'draft' and order.subscription_status == 'draft':
                # We keep the subscription state 1_draft to keep the subscription quotation in the subscription app
                # quotation view.
                #    order.subscription_status = '2_renewal' if order.subscription_id else '1_draft'
                order.subscription_status = 'draft'
            else:
                order.subscription_status = False
                
    def _group_expand_states(self, states, domain, order):
        return ['progress', 'close']


    @api.depends('date_start', 'state', 'date_next_invoice')
    def _compute_last_invoice_date(self):
        for order in self:
            last_date = order.next_invoice_date and order.plan_id.billing_period and order.next_invoice_date - order.plan_id.billing_period
            start_date = order.start_date or fields.Date.today()
            if order.state == 'sale' and last_date and last_date >= start_date:
                # we use get_timedelta and not the effective invoice date because
                # we don't want gaps. Invoicing date could be shifted because of technical issues.
                order.last_invoice_date = last_date
            else:
                order.last_invoice_date = False

    @api.depends('subscription_order', 'state', 'date_start', 'subscription_status')
    def _compute_next_invoice_date(self):
        for so in self:
           if not so.date_next_invoice and so.state == 'sale':
                so.date_next_invoice = so.date_start or fields.Date.today()

    def _compute_start_date(self):
        for so in self:
            if not so.subscription_order:
                so.date_start = False
            elif not so.date_start:
                so.date_start = fields.Date.today()
                
    @api.depends('date_start')
    def _compute_contact_start_date(self):
        for so in self:
            so.date_first_contract = so.date_start
                
    # =========================================================================
    # ============================ Action Button ==============================
    # =========================================================================
    def action_confirm(self):
        """Update and/or create subscriptions on order confirmation."""
        recurring_order = self.env['sale.order']
        for order in self:
            res_sub = super(SubscriptionOrder, self).action_confirm()
            order.write({
                'subscription_status': 'progress',
            })

        return res_sub
        
    