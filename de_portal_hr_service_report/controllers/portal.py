# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from operator import itemgetter
from odoo.addons.de_portal_hr_service.common import (import_data)

from markupsafe import Markup
from math import ceil
from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, UserError, ValidationError

from odoo.http import request
from odoo.tools.translate import _
from odoo.tools import groupby as groupbyelem
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager
from odoo.osv.expression import OR, AND
import base64
from odoo.tools import safe_eval
from collections import OrderedDict
from itertools import dropwhile
import json

class CustomerPortal(portal.CustomerPortal):
    
    def _prepare_report_record_page(self,report_id, model_id, record_id, edit_mode,result_html):
        m2o_id = False
        # extra_template = ''
        primary_template = ''
        # rec_id = 0
        record_id = request.env['hr.service.report'].sudo().search([('id','=',report_id)],limit=1)
        # hr_service_items = False
        record_sudo = False
        record_val = ''
        
        field_val = ''
        field_domain = []
        
        hr_report_items = None
        if record_id.model_id.id == int(model_id):
            hr_report_items = record_id.param_field_ids

    
        
        # ------------------------------------------
        # ------------- Left Section ----------------
        # ------------------------------------------
    
        primary_template += '<link href="/de_portal_hr_service/static/src/datatable.css" rel="stylesheet" />'
        primary_template += '<link href="/de_portal_hr_service/static/src/select_two.css" rel="stylesheet" />'
        primary_template += '<link href="/de_portal_hr_service/static/src/datatable_export_button.css" rel="stylesheet" />'

        primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/jquery.js"></script>'
        primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/select_two.js"></script>'
        primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/dynamic_form.js"></script>'

        primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/datatable.js"></script>'
        primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_buttons.js"></script>'
        primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_jszip.js"></script>'
        primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_pdfmake.js"></script>'
        primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_vfs_fonts.js"></script>'
        primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_btn_html5.js"></script>'
        primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_print.js"></script>'
        primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_select.js"></script>'
        primary_template += '<script type="text/javascript" src="/de_portal_hr_service_report/static/src/js/main_datatable.js"></script>'
        primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/sweetalert.js"></script>'
        primary_template += '<div class="col-lg-12 text-left mb16" style="padding:0px;border-bottom:1px solid #cccccc;"><h1>' + record_id.name + '</h1></div>'

        primary_template += '<section class="col-lg-12" style="padding:16px;">'
        
        primary_template += "<div class='card bg-light mx-3 my-3  p-3  bg-white' style='padding:16px;background-color:#FFFFFF; border-radius: 15px;'>"
        primary_template += '<div class="border border-1 p-3 border-opacity-10" style=" border-radius: 10px;">'
        for report in record_id:
        
            primary_template += "<div class='row'>"

            for field in hr_report_items:
                field_domain = []
                primary_template += "<div class='form-group col-6' data-type='char' data-name='" + field.name + "'>"
                
                primary_template += "<label class='s_website_form_label' style='width: 200px' for='" + field.name + "'>"
                primary_template += "<span class='s_website_form_label_content'>" + field.field_description + "</span>"
                primary_template += "</label>"
            
                # Many2one Field
                if field.ttype == 'many2one':
                    m2o_id = request.env[field.relation].sudo().search(field_domain)
                    primary_template += "<select id='" + field.name + "' name='" + field.name + "'class='form-control selection-search'>"

                    for m in m2o_id:
                        primary_template += "<option value='" + str(m.id) + "' " + (" selected" if record_val == m.id else " ") + ">"
                        primary_template += m.name
                        primary_template += "</option>"
                    primary_template += "</select>"
                        
                # Many2many field
                elif field.ttype == 'many2many':
                    m2m_id = request.env[field.model].sudo().search([])
                    primary_template += "<select id='" + field.name + "' name='" + field.name + "'class='form-control selection-search' multiple='multiple'>"
                    for m in m2m_id:
                        primary_template += "<option value='" + str(m.id) + "' " + (" selected" if record_val == m.id else " ") + ">"
                        primary_template += m.name
                        primary_template += "</option>"
                    primary_template += "</select>"

                # Selection field
                elif field.ttype == 'selection':
                    sel_ids = request.env['ir.model.fields.selection'].sudo().search([('field_id','=',field.id)])
                    primary_template += "<select id='" + field.name + "' name='" + field.name + "'class='form-control' >"
                    for sel in sel_ids:
                        primary_template += "<option value='" + str(sel.value) + "' " + (" selected" if str(record_val) == sel.value else " ") + ">"
                        primary_template += sel.name
                        primary_template += "</option>"
                    primary_template += "</select>"
            
                # Date Field
                elif field.ttype == 'date':
                    primary_template += '<input type="date" class="form-control s_website_form_input"' + 'name="' + field.name + '"' + ' id="' + field.name + '"' + 'value="' + record_val + '"' +    ">"
                elif field.ttype == 'datetime':
                    primary_template += '<input type="datetime-local" class="form-control s_website_form_input"' + 'name="' + field.name + '"' + ' id="' + field.name + '"' + 'value="' + record_val + '"' +    ">"
                elif field.ttype == 'char':
                    primary_template += '<input type="text" class="form-control s_website_form_input"' + 'name="' + field.name + '"' + ' id="' + field.name + '"' + 'value="' + record_val + '"'  + ">"
                elif field.ttype == 'text':
                    primary_template += '<textarea class="form-control s_website_form_input"' + 'name="' + field.name + '"' + ' id="' + field.name + '"' + 'value="' + record_val + '"' +    " ></textarea>"
                elif field.ttype in ('integer','float','monetary'):
                    primary_template += '<input type="number" class="form-control s_website_form_input"' + 'name="' + field.name + '"' + ' id="' + field.name + '"' + 'value="' + record_val + '"' +    ">"
                else:
                    primary_template += '<input type="text" class="form-control s_website_form_input"' + 'name="' + field.name + '"' + ' id="' + field.name + '"' + 'value="' + record_val + '"' +    ">"
                primary_template += "</div>"
                        
            # add seperator and button
            primary_template += '<div class="form-group col-12 s_website_form_submit" data-name="Submit Button" style="text-align: right;">'
            primary_template += '<hr class="w-100 mx-auto" style="border-top-width: 1px; border-top-style: solid;"/>'
           
            primary_template += '<div class="row"/>'
            primary_template += '<div class="d-flex flex-row col-6"/>'
            primary_template += '<button type="button" class="btn btn-link p-0 m-0 text-decoration-none" onclick="window.history.back();"  style="text-align: left;">Back</button>'
            

            primary_template += '<span id="s_website_form_result_back"/>'
            primary_template += '</div>'
            primary_template += '<div class="d-flex flex-row-reverse col-6"/>'
            primary_template += '<button type="submit" class="btn btn-primary">Submit</button>'
            primary_template += '<span id="s_website_form_result"/>'
            primary_template += '</div>'
            primary_template += '</div>'


            primary_template += "</div>"
            primary_template += "</div>"
            primary_template += "</section>"


            primary_template += "<div id = 'data_table_div' class='col-lg-12 text-left mb16' style='padding:0px;border-bottom:1px solid #cccccc;'>"
            primary_template += "</div>"


        
        if result_html:
            primary_template += result_html

        
        # ------------------------------------------
        # -------------Right Section Fields ----------------
        # ------------------------------------------
   
        currency_ids = request.env['res.currency'].sudo().search([('active','=',True)])
        data =  {
            'currency_ids': currency_ids,
            'template_primary_fields': primary_template,
            # 'template_extra_fields': extra_template,
            'report_id': report_id,
            'record_id': record_id.id,
            'model_id': model_id,
            'edit_mode': edit_mode or 0,
        }
        return data

        
    # @http.route(['/my/report/model/record/prev/<int:service_id>/<int:model_id>/<int:record_id>'
    #             ], type='http', auth="user", website=True)        
    # def portal_hr_report_record_previous(self, service_id=False, model_id=False, record_id=False, edit_mode=False, **kw):
    #     return request.render("de_portal_hr_service_report.portal_report_record_form", self._prepare_report_record_page(service_id, model_id, record_id, edit_mode))
        
    
    @http.route('/my/report/model/record/submit', website=True, page=True, auth='public', csrf=False)
    def hr_report_record_submit(self, **kw):
        report_id = request.env['hr.service.report'].sudo().search([('id','=',(kw.get('report_id')))],limit=1)
        query = report_id.sql_text
        inputs  = []
        x_keys = {k:v for k, v in kw.items() if k.startswith("x_")}

        if query:
            headers = []
            datas = []
            params = inputs
            try:
                request.env.cr.execute(query,x_keys)
            except Exception as e:
                raise UserError(e)
            try:
                if request.env.cr.description:
                    headers = [d[0] for d in request.env.cr.description]
                    datas = request.env.cr.fetchall()
            except Exception as e:
                raise UserError(e)
            template = ''
            if headers and datas:

                template += '<link href="/de_portal_hr_service/static/src/datatable.css" rel="stylesheet" />'
                template += '<link href="/de_portal_hr_service/static/src/select_two.css" rel="stylesheet" />'
                template += '<link href="/de_portal_hr_service/static/src/datatable_export_button.css" rel="stylesheet" />'

                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/jquery.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/select_two.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/dynamic_form.js"></script>'

                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/datatable.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_buttons.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_jszip.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_pdfmake.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_vfs_fonts.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_btn_html5.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_print.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_select.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service_report/static/src/js/main_datatable.js"></script>'

                template += '<section class="col-lg-12" style="padding:16px;">'
                template += '<button type="button" class="mx-4 my-0 btn btn-link p-0 m-0 text-decoration-none" onclick="window.history.back();"  style="text-align: left;">Back</button>'

                template += "<div class='card bg-light mx-3 my-3  p-3  bg-white' style='padding:16px;background-color:#FFFFFF; border-radius: 15px;'>"
                template += '<div class="border border-1 p-3 border-opacity-10" style=" border-radius: 10px;">'


                template += "<table class='myTable mt-2 cell-border '>"
                template += "<thead class='bg-100'>"
                for header in headers:
                    template += "<th>" + header + "</th>"
                template += "</thead>"

                template += "<tbody class='sale_tbody'>"
                for data in datas:
                    template += "<tr>"
                    for value in data:
                        if value is not None:
                            display_value = str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                            template += "<td style='text-overflow: clip;'>{0}</td>".format(display_value)
                    template += "</tr>"
                template += "</tbody>"
                template += "</table>"
                template += "</div>"
                template += "</div>"
                template += "</section>"
                data =  {
                    'template_primary_fields': template,
             
                }    
                return request.render("de_portal_hr_service_report.portal_report_result", data)
            template += '<script type="text/javascript">swal({title: "Results",text: "No Data found",buttons: false,timer: 1500,}); </script>'
            return request.render("de_portal_hr_service_report.portal_report_record_form", self._prepare_report_record_page(report_id.id, report_id.model_id.id, 0, 0,template))
