import binascii
import werkzeug

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment import utils as payment_utils
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager


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
            ('subscription_status', 'in', ['progress', 'paused', 'close']),
            ('subscription_order', '=', True)
        ]

    def _prepare_sale_subscription_portal_rendering_values(
        self, page=1, date_begin=None, date_end=None, sortby=None,  quotation_page=False, **kwargs
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
        
    @http.route([
        '/my/suborders', 
        '/my/suborders/page/<int:page>',
        '/my/suborder'
    ], type='http', auth="user", website=True)
    def portal_my_subscription_orders(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kwargs):
        values = self._prepare_sale_subscription_portal_rendering_values(quotation_page=False, **kwargs)
        request.session['my_subscription_orders_history'] = values['subscription_orders'].ids[:100]
        return request.render("de_subscription.portal_my_subscription_orders", values)

    # Subscription Page Controller
    @http.route([
        '/my/suborders/<int:order_id>',
        '/my/suborders/<int:order_id>/<access_token>',
    ], type='http', auth="public", website=True)
    def portal_subscription_order_page(
        self,
        order_id,
        report_type=None,
        access_token=None,
        message=False,
        download=False,
        downpayment=None,
        **kw
    ):
        subscription_sudo, redirection = self._get_subscription_order(access_token, order_id)
        if redirection:
            return redirection
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(
                model=subscription_sudo,
                report_type=report_type,
                report_ref='sale.action_report_saleorder',
                download=download,
            )

        backend_url = f'/web#model={subscription_sudo._name}'\
                      f'&id={subscription_sudo.id}'\
                      f'&action={subscription_sudo._get_portal_return_action().id}'\
                      f'&view_type=form'
        
        values = {
            'subscription_order': subscription_sudo,
            'sale_order': subscription_sudo,
            'product_documents': subscription_sudo._get_product_documents(),
            'message': message,
            'report_type': 'html',
            'default_url': '/my/suborders',
            'backend_url': backend_url,
            'res_company': subscription_sudo.company_id,  # Used to display correct company logo
        }

        history_session_key = 'my_subscriptions_history'

        values = self._get_page_view_values(
            subscription_sudo, access_token, values, history_session_key, False)

        return request.render('de_subscription.sale_subscription_order_portal_template', values)
        #return request.render('sale.sale_order_portal_template', values)

    def _get_subscription_order(self, access_token, order_id):
        logged_in = not request.env.user.sudo()._is_public()
        order_sudo = request.env['sale.order']
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token)
        except AccessError:
            if not logged_in:
                subscription_url = '/my/suborders/%d' % order_id
                return order_sudo, werkzeug.utils.redirect('/web/login?redirect=%s' % werkzeug.urls.url_quote(subscription_url))
            else:
                raise werkzeug.exceptions.NotFound()
        except MissingError:
            return order_sudo, request.redirect('/my')
        return order_sudo, None

    def _prepare_quotations_domain(self, partner):
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('subscription_order','=',False),
            ('state', '=', 'sent')
        ]

    def _prepare_orders_domain(self, partner):
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('subscription_order','=',False),
            ('state', '=', 'sale'),
        ]

    # Renew Subscription
    @http.route(['/my/suborders/renew/<int:order_id>'
                ], type='http', auth="user", website=True)        
    def renew_subscription(
        self,
        order_id,
        report_type=None,
        access_token=False,
        message=False,
        download=False,
        downpayment=None,
        **kw
    ):
        return request.redirect(f'/my/suborders/{order_id}?access_token={access_token}')
        #return request.render("de_portal_hr_service.portal_service_record_form", self._prepare_service_record_page(service_id, model_id, record_id, edit_mode, js_code))
    