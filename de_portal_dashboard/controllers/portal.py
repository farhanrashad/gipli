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
import json
from odoo.osv import expression

class CustomerPortal(CustomerPortal):
    
    @http.route('/my/services/dashboard', type='http', auth='public', website=True, csrf=False)
    def my_services_dashboard(self, **kwargs):
        dash_item_ids = request.env['base.dashboard.item'].search([])

        output_html = '''
            <div class="container">
                <div class="row">
        '''
        for item in dash_item_ids:
            records = request.env[item.model_id.model].search([])
            output_html += '''
                <div class="col-lg-6">
                    <div class="card mb-3">
                        <div class="card-body">
                            <h5 class="card-title">{item_name}</h5>
                            <table class="table table-striped">
            '''.format(item_name=item.name)
            
            for record in records:
                output_html += '<tr>'
                for field in item.field_ids:
                    output_html += '''
                        <td>{record_value}</td>
                    '''.format(
                        record_value=getattr(record, field.name, '')
                    )
                output_html += '</tr>'
            output_html += '''
                            </table>
                        </div>
                    </div>
                </div>
            '''
        output_html += '''
                </div>
            </div>
        '''

        values = {
            'output_html': output_html,
        }
        return request.render("de_portal_dashboard.portal_services_dashboard", values)