# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment import utils as payment_utils
#from odoo.addons.payment.controllers import portal as subscription_portal
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import pager as portal_pager


#class CustomerPortal(subscription_portal.SubscriptionPortal):
class SubscriptionCustomerPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        Subscription = request.env['sale.order']
        
        if 'subscription_count' in counters:
            values['subscription_count'] = Subscription.search_count(self._prepare_subscription_orders_domain(partner), limit=1) \
                if Subscription.check_access_rights('read', raise_exception=False) else 0

        return values

    def _prepare_subscription_orders_domain(self, partner):
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', '=', 'sale'),
        ]

    def _prepare_sale_subscription_portal_rendering_values(
        self, page=1, date_begin=None, date_end=None, sortby=None, subscription_page=False, **kwargs
    ):
        SubscriptionOrder = request.env['sale.order']

        if not sortby:
            sortby = 'date'

        partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()

        url = "/my/suborders"
        domain = self._prepare_subscription_orders_domain(partner)

        searchbar_sortings = self._get_sale_subscription_searchbar_sortings()

        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        pager_values = portal_pager(
            url=url,
            total=SubscriptionOrder.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
        )
        subscriptions = SubscriptionOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager_values['offset'])

        values.update({
            'date': date_begin,
            'subscription_orders': subscriptions.sudo(),
            'page_name': 'subscription_order',
            'pager': pager_values,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return values

    def _get_sale_subscription_searchbar_sortings(self):
        return {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        
    @http.route(['/my/suborders', '/my/suborders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_subscription_orders(self, **kwargs):
        values = self._prepare_sale_subscription_portal_rendering_values(quotation_page=False, **kwargs)
        request.session['my_subscription_orders_history'] = values['subscription_orders'].ids[:100]
        return request.render("de_subscription.portal_my_subscription_orders", values)