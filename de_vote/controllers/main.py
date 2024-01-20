# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from datetime import datetime
import base64
import logging

_logger = logging.getLogger(__name__)


class CustomerPortal(http.Controller):
    
    @http.route('/search/candidate', type='http', auth="public", website=True)
    def candidate_form(self, **kw):
        return request.render("de_vote.search_candidate_form", self._prepare_search_form_page())
    
    @http.route(['/search/candidate/list'],type="http", auth="public", website=True)
    def search_candidate(self, **kw):
        #return request.redirect('/search/candidate')
        const_id = kw.get('select_const')
        return request.render("de_vote.candidate_list",self._prepare_candidate_list_page(const_id))

    
    
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

    def _prepare_candidate_list_page(self, const_id):
        html_code = ""
        const = request.env['vote.const'].sudo().search([('id','=',const_id)])
        member_ids = request.env['vote.elect.member'].sudo().search([('const_id','=',const.id)])
        #html_code += "<h3> Member's List of " + const.name + "</h3>"
        #html_code += "<h3> Member's List of " + str(const_id) + str(member_ids) + "</h3>"

        # Candidate List
        #for member in member_ids:
        #    html_code += "<h3>  " + str(member.contact_name) + "</h3>"


            

        #    if member.pol_partner_id.image_1920:
        #        image_base64 = base64.b64encode(member.pol_partner_id.image_1920).decode('utf-8')
                # Include the image in the HTML code
                #html_code += '<img src="data:image/png;base64,' + image_base64 + '" alt="' + member.contact_name + '"/>'
                #html_code += '<img src="' + image_base64 + '" t-options="{"widget": "image"}"/>'
                #html_code += '<img name="profile" t-att-src="image_data_uri(member.pol_partner_id.image_1920)" class="card-img-top" alt="" width="10%" data-mimetype="image/png"/>'
                #html_code += "<img t-att-src=" + "'" + "/web/image/vote.elect.member/%s/image" + "'" + "%" + str(member.id) + " alt='Student'/>"

        
        return {
            'search_form_code': html_code,
            'const_name': const.name,
            'members': member_ids,
        }
    