# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from datetime import datetime


class CustomerPortal(http.Controller):
    
    @http.route('/search/candidate', type='http', auth="public", website=True)
    def candidate_form(self, **kw):
        return request.render("de_vote.search_candidate_form", self._prepare_search_form_page())
    
    @http.route(['/search/candidate/list'],type="http", auth="public", website=True)
    def search_candidate(self, **kw):
        #return request.redirect('/search/candidate')
        return request.render("de_vote.candidate_list")

    
    
    def _prepare_search_form_page(self):
        html_code = ""
        const_ids = request.env['vote.const'].sudo().search([('const_type_id','=',1)])
        html_code += "<div class='container pt32'>"
        html_code += "<div class='row'>"
        html_code += "<div class='col-12 ' ><h3>Select Constituency</h3></div>"
        html_code += "<div class='col-6 ' >"
        html_code += "<select name='select_const' id='select_const' class='selection-search form-control' >"
        for const_id in const_ids:
            html_code += "<option value='" + str(const_id.id) + "'>" + const_id.name
            html_code += "</option>"
        html_code += "</select>"
        html_code += '<button type="submit" class="btn btn-primary">Submit</button>'
        html_code += '<span id="s_website_form_result"/>'
        html_code += "</div>"
        html_code += "</div>"
        html_code += "</div>"
        
        return {
            'search_form_code': html_code,
        }
    