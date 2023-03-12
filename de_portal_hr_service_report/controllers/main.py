# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
from operator import itemgetter

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, UserError, ValidationError
from odoo.http import request
#from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

from odoo.tools import groupby as groupbyelem
from odoo.tools import safe_eval

from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'report_count' in counters:
            domain = [('state','=','publish')]
            values['report_count'] = request.env['hr.service.report'].search_count(domain) \
                if request.env['hr.service.report'].check_access_rights('read', raise_exception=False) else 0
        return values
    
    
    # ------------------------------------------------------------
    # My Services
    # ------------------------------------------------------------
    def _report_get_page_view_values(self, report, access_token, **kwargs):
        values = {
            'page_name': 'report',
            'report': report,
        }
        return self._get_page_view_values(report, access_token, values, 'my_reports_history', False, **kwargs)
    
    @http.route(['/my/reports'], type='http', auth="user", website=True)
    def portal_my_hr_services(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        report = request.env['hr.service.report']
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # Report count
        report_count = report.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/reports",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=report_count,
            page=page,
            step=self._items_per_page
        )
        domain += [('state','=','publish')]
        # content according to pager and archive selected
        reports = report.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_reports_history'] = reports.ids[:100]
        
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'reports': reports,
            'page_name': 'report',
            'default_url': '/my/reports',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("de_portal_hr_service_report.portal_my_hr_report_list", values)
    
    
    
    def _report_records_get_page_view_values(self, report, access_token, **kwargs):
        values = {
            'page_name': 'records',
            'report': report,
        }
        return self._get_page_view_values(report, access_token, values, 'my_reports_history', False, **kwargs)
    
   
    @http.route(['/my/report/<int:report_id>'], type='http', auth="public", website=True)
    def portal_my_hr_report(self, report_id=None, access_token=None, **kw):
        try:
            report_sudo = self._document_check_access('hr.service.report', report_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        return request.render("de_portal_hr_service_report.portal_report_record_form", self._prepare_report_record_page(report_sudo.id, report_sudo.model_id.id, 0, 0,''))
        

 