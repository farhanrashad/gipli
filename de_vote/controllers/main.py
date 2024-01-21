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
        na_code = pa_code = ""
        const_ids = request.env['vote.const'].sudo().search([('const_type_id.code','=','NA')],order='sequence')
        pa_const_ids = request.env['vote.const'].sudo().search([('const_type_id.code','=','PA')],order='sequence')


        #National Constituency
        na_code += "<div class='container pt32'>"
        #na_code += "<div class='row'>"
        na_code += "<div class='col-lg-10 ' >"
        na_code += "<h4>National Constituency</h4>"
        na_code += "<div class='s_col_no_resize s_col_no_bgcolor pt8 pb8' >"
        #na_code += '<label class="col-form-label col-sm-auto s_website_form_label" style="width: 200px" for="studio1"><span class="s_website_form_label_content">National Constituency</span></label>'
        #na_code += "<div class='col-sm'>"
        na_code += "<select name='select_const' id='select_const' class='selection-search form-control' >"
        for const_id in const_ids:
            na_code += "<option value='" + str(const_id.id) + "'>" + const_id.name
            na_code += "</option>"
        na_code += "</select>"
        na_code += '<div style="width: 200px;" class="s_website_form_label pt16"></div>'
        na_code += '<button type="submit" class="btn btn-primary">Search</button>'
        na_code += "</div>"
        #na_code += "</div>"
        na_code += '<span id="s_website_form_result"/>'
        na_code += "</div>"
        na_code += "</div>"
        #na_code += "</div>"

        # Provincial Constituency
        pa_code += "<div class='container pt32'>"
        #pa_code += "<div class='row'>"
        pa_code += "<div class='col-lg-10' >"
        pa_code += "<h4>Provincial Constituency</h4>"        
        pa_code += "<div class='s_col_no_resize s_col_no_bgcolor pt8 pb8' >"
        #pa_code += '<label class="col-form-label col-sm-auto s_website_form_label" style="width: 200px" for="studio1"><span class="s_website_form_label_content">Provincial Constituency</span></label>'
        #pa_code += "<div class='col-sm'>"
        pa_code += "<select name='select_const' id='select_const' class='selection-search form-control' >"
        for const_id in pa_const_ids:
            pa_code += "<option value='" + str(const_id.id) + "'>" + const_id.name
            pa_code += "</option>"
        pa_code += "</select>"
        pa_code += '<div style="width: 200px;" class="s_website_form_label pt16"></div>'
        pa_code += '<button type="submit" class="btn btn-primary">Search</button>'
        pa_code += "</div>"
        #pa_code += "</div>"
        pa_code += '<span id="s_website_form_result"/>'
        pa_code += "</div>"
        #html_code += '</form>'
        
        pa_code += "</div>"
        #pa_code += "</div>"
        
        return {
            'na_search_form_code': na_code,
            'pa_search_form_code': pa_code,
        }

    def _prepare_candidate_list_page(self, const_id):
        const = request.env['vote.const'].sudo().search([('id','=',const_id)])
        member_ids = request.env['vote.elect.member'].sudo().search([('const_id','=',const.id)])

        if const.const_type_id.code == 'NA':
            related_const_ids = request.env['vote.const'].sudo().search([('parent_id','=',const.id)])
            related_const_member_ids = request.env['vote.elect.member'].sudo().search([('const_id','in',related_const_ids.ids)])
        elif const.const_type_id.code == 'PA':
            related_const_id = request.env['vote.const'].sudo().search([('id','=',const.id)])
            related_const_member_ids = request.env['vote.elect.member'].sudo().search([('const_id','=',related_const_id.parent_id.id)])
        
        return {
            'const_name': const.name,
            'members': member_ids,
            'related_const_members': related_const_member_ids,
        }
    