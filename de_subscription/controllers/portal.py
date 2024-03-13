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
        
        if 'subscription_order_count' in counters:
            values['subscription_order_count'] = Subscription.search_count(self._prepare_subscription_orders_domain(partner), limit=1) \
                if Subscription.check_access_rights('read', raise_exception=False) else 0

        return values

    def _prepare_subscription_orders_domain(self, partner):
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', '=', 'sale'),
        ]

    def _prepare_sale_subscription_portal_rendering_values(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kwargs
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
        values = self._prepare_sale_subscription_portal_rendering_values(**kwargs)
        request.session['my_subscription_orders_history'] = values['subscription_orders'].ids[:100]
        return request.render("de_subscription.portal_my_subscription_orders", values)

    # Subscription Page Controller
    @http.route(['/my/suborders/<int:subscription_order_id>'], type='http', auth="public", website=True)
    def portal_subscription_order_page(
        self,
        subscription_order_id,
        report_type=None,
        access_token=None,
        message=False,
        download=False,
        downpayment=None,
        **kw
    ):
        try:
            subscription_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(
                model=subscription_sudo,
                report_type=report_type,
                report_ref='sale.action_report_saleorder',
                download=download,
            )

        if request.env.user.share and access_token:
            # If a public/portal user accesses the order with the access token
            # Log a note on the chatter.
            today = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_quote_%s' % subscription_sudo.id)
            if session_obj_date != today:
                # store the date as a string in the session to allow serialization
                request.session['view_quote_%s' % subscription_sudo.id] = today
                # The "Quotation viewed by customer" log note is an information
                # dedicated to the salesman and shouldn't be translated in the customer/website lgg
                context = {'lang': subscription_sudo.user_id.partner_id.lang or subscription_sudo.company_id.partner_id.lang}
                msg = _('Quotation viewed by customer %s', subscription_sudo.partner_id.name if request.env.user._is_public() else request.env.user.partner_id.name)
                del context
                _message_post_helper(
                    "sale.order",
                    subscription_sudo.id,
                    message=msg,
                    token=subscription_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=subscription_sudo.user_id.sudo().partner_id.ids,
                )

        backend_url = f'/web#model={subscription_sudo._name}'\
                      f'&id={subscription_sudo.id}'\
                      f'&action={subscription_sudo._get_portal_return_action().id}'\
                      f'&view_type=form'
        values = {
            'subscription_order': subscription_sudo,
            'product_documents': subscription_sudo._get_product_documents(),
            'message': message,
            'report_type': 'html',
            'backend_url': backend_url,
            'res_company': subscription_sudo.company_id,  # Used to display correct company logo
        }

        # Payment values
        if subscription_sudo._has_to_be_paid():
            values.update(
                self._get_payment_values(
                    subscription_sudo,
                    downpayment=downpayment == 'true' if downpayment is not None else subscription_sudo.prepayment_percent < 1.0
                )
            )

        if subscription_sudo.state in ('draft', 'sent', 'cancel'):
            history_session_key = 'my_quotations_history'
        else:
            history_session_key = 'my_orders_history'

        values = self._get_page_view_values(
            subscription_sudo, access_token, values, history_session_key, False)

        return request.render('sale.sale_order_portal_template', values)