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
    
    subscription_order = fields.Boolean("Subscription")
    subscription_status = fields.Selection([
        ('draft', 'Quotation'),  # Quotation for a new subscription
        #('renew', 'Renewal Quotation'),  # Renewal Quotation for existing subscription
        ('progress', 'In Progress'),  # Active Subscription or confirmed renewal for active subscription
        #('block', 'Paused'),  # Active subscription with paused invoicing
        ('renewed', 'Renewed'),  # Active or ended subscription that has been renewed
        ('close', 'Close'),  # Closed or ended subscription
        #('cancel', 'Cancel'),  # Closed or ended subscription
        #('7_upsell', 'Upsell'),  # Quotation or SO upselling a subscription
    ], 
        string='Subscription Status', compute='_compute_subscription_status', store=True, index='btree_not_null', tracking=True, group_expand='_group_expand_states',
    )

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
            #elif order.subscription_order or order.state == 'draft' and order.subscription_status == 'draft':
                # We keep the subscription state 1_draft to keep the subscription quotation in the subscription app
                # quotation view.
            #    order.subscription_status = '2_renewal' if order.subscription_id else '1_draft'
            else:
                order.subscription_status = False
                
    def _group_expand_states(self, states, domain, order):
        return ['progress', 'block']
    