# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, date
from odoo import api, fields, models, _
from odoo.tools import float_compare, format_datetime, format_time
from pytz import timezone, UTC
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


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

    subscription_type = fields.Selection([
        ('normal', 'Normal'),
        ('renewal', 'Renewal'),  
        ('upsell', 'Upsell'),  
        ('revised', 'Revision'),
        ('close', 'Close'),
    ], 
        string='Subscription Type', default="normal",
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
                             compute='_compute_date_start',
                             readonly=False,
                             store=True,
                             tracking=True,
                             help="The start date indicate when the subscription periods begin.")
    
    date_end = fields.Date(string='End Date', tracking=True,
                           compute='_compute_date_end',
                           readonly=False,
                           store=True,
                           help="If set in advance, the subscription will be set to renew 1 month before the date and will be closed on the date set in this field.")
    date_first_contract = fields.Date(
        compute='_compute_contact_start_date',
        store=True,
        help="The first contract date is the start date of the first contract of the sequence. It is common across a subscription and its renewals.")

    parent_subscription_id = fields.Many2one('sale.order', string='Parent Contract', ondelete='restrict', copy=False)
    subscription_line_ids = fields.One2many('sale.order', 'parent_subscription_id')

    # Count Fields
    count_past_subscriptions = fields.Integer(compute='_compute_past_subscriptions')
    count_upselling_subscriptions = fields.Integer(compute='_compute_upselling_count')
    count_renewal_subscriptions = fields.Integer(compute="_compute_renewal_count")
    count_revised_subscriptions = fields.Integer(compute="_compute_revised_count")

    
    # =======================================================================
    # ========================== Computed Mehtods ===========================
    # =======================================================================

    def _compute_past_subscriptions(self):
        for order in self:
            subscription_ids = self.env['sale.order'].search([('parent_subscription_id', '=', order.id)])
            order.count_past_subscriptions = len(subscription_ids)

    def _compute_upselling_count(self):
        self.count_upselling_subscriptions = 2

    def _compute_renewal_count(self):
        self.count_renewal_subscriptions = 2

    def _compute_revised_count(self):
        self.count_revised_subscriptions = 2
        
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
            last_date = order.date_next_invoice and order.subscription_plan_id.billing_period and order.date_next_invoice - order.subscription_plan_id.billing_period
            date_start = order.date_start or fields.Date.today()
            if order.state == 'sale' and last_date and last_date >= date_start:
                # we use get_timedelta and not the effective invoice date because
                # we don't want gaps. Invoicing date could be shifted because of technical issues.
                order.date_last_invoice = last_date
            else:
                order.date_last_invoice = False

    @api.depends('subscription_order', 'state', 'date_start', 'subscription_status')
    def _compute_next_invoice_date(self):
        for so in self:
           if not so.date_next_invoice and so.state == 'sale':
                so.date_next_invoice = so.date_start or fields.Date.today()

    @api.depends('subscription_order', 'state', 'subscription_status','subscription_plan_id')
    def _compute_date_start(self):
        for so in self:
            if not so.subscription_order:
                so.date_start = False
            elif not so.date_start:
                    so.date_start = fields.Date.today()

    @api.depends('date_start','subscription_plan_id')
    def _compute_date_end(self):
        for so in self:
            if not so.subscription_order:
                so.date_end = False
            elif not so.date_end:
                    kwargs = {so.subscription_plan_id.recurring_interval_type+"s": so.subscription_plan_id.intervals_total}
                    date_end = so.date_start + relativedelta(**kwargs)
                    so.date_end = date_end
                
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

    def button_operations(self):
        self.ensure_one()
        return {
            'name': 'Operations',
            'view_mode': 'form',
            'res_model': 'sale.sub.op.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            
        }

    def open_subscription_renewal(self):
        return {
            'name': 'Renewed Subscriptions',
            'view_mode': 'tree',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('parent_subscription_id','=',self.id),('subscription_type','==','renewal')],
            'action_id': self.env.ref('de_subscription.action_subscription_order').id,
        }

    def open_subscription_upsell(self):
        return {
            'name': 'Upselling Subscriptions',
            'view_mode': 'tree',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('parent_subscription_id','=',self.id),('subscription_type','==','upsell')],
            'action_id': self.env.ref('de_subscription.action_subscription_order').id,
        }

    def open_past_subscriptions(self):
        return {
            'name': 'Upselling Subscriptions',
            'view_mode': 'tree',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('parent_subscription_id','=',self.id)],
            'action_id': self.env.ref('de_subscription.action_subscription_order').id,
        }

    def open_revised_subscriptions(self):
        return {
            'name': 'Upselling Subscriptions',
            'view_mode': 'tree',
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'domain': [('parent_subscription_id','=',self.id),('subscription_type','==','revised')],
            'action_id': self.env.ref('de_subscription.action_subscription_order').id,
        }
        
    