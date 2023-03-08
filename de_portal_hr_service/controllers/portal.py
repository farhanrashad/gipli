# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from operator import itemgetter
from odoo.addons.de_portal_hr_service.common import (import_data)

from markupsafe import Markup

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, UserError, ValidationError

from odoo.http import request
from odoo.tools.translate import _
# from odoo.tools import groupby as groupbyelem
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager
from odoo.osv.expression import OR, AND
import base64
from odoo.tools import safe_eval
from collections import OrderedDict
from itertools import dropwhile
from itertools import groupby

#from odoo.addons.website.controllers import form



import json

class CustomerPortal(portal.CustomerPortal):
    
    def _prepare_service_record_page(self,service_id, model_id, record_id, edit_mode):
        m2o_id = False
        extra_template = ''
        primary_template = ''
        rec_id = 0
        #record_id = 0
        service_id = request.env['hr.service'].sudo().search([('id','=',service_id)],limit=1)
        hr_service_items = False
        record_sudo = False
        record_val = ''
        
        field_val = ''
        field_domain = []
        
        line_item = request.env['hr.service.record.line'].search([('hr_service_id','=',service_id.id),('line_model_id','=',int(model_id))],limit=1)
        
        if service_id.header_model_id.id == int(model_id):
            #record_id = request.env[service_id.header_model_id.model].sudo().search([('id','=',int(rec_id))],limit=1).id
            hr_service_items = service_id.hr_service_items
            if edit_mode == '1' or edit_mode == 1:
                record_sudo = request.env[service_id.header_model_id.model].sudo().search([('id','=',record_id)],limit=1)
            
            #primary_template += '<div class="col-lg-12 text-left mb16" style="border-bottom:1px solid #cccccc;"><h5>' + service_id.header_model_id.name + '</h5></div>'
            #extra_template += "<br/>"
            
        #elif service_id.line_model_id.id == int(model_id):
        elif line_item:
            #record_id = request.env[service_id.line_model_id.model].sudo().search([('id','=',int(rec_id))],limit=1).id
            #hr_service_items = line_model_id.hr_service_record_line_items #service_id.hr_service_items_line
            hr_service_items = line_item.hr_service_record_line_items
            if edit_mode == '1' or edit_mode == 1:
                record_sudo = request.env[line_item.line_model_id.model].sudo().search([('id','=',record_id)],limit=1)
            
            #primary_template += '<div class="col-lg-12 text-left mb16" style="border-bottom:1px solid #cccccc;"><h5>' + service_id.header_model_id.name + ' / ' + str(line_item.line_model_id.name) + '</h5></div>'
            #extra_template += "<br/>"
            

                
        
        # ------------------------------------------
        # ------------- Left Section ----------------
        # ------------------------------------------
        for service in service_id:

            primary_template += '<link href="/de_portal_hr_service/static/src/select_two.css" rel="stylesheet" />'
            primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/jquery.js"></script>'
            primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/select_two.js"></script>'
            primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/dynamic_form.js"></script>'

                        

                        
            primary_template += '<div class="col-lg-12 text-left mb16" style="padding:0px;border-bottom:1px solid #cccccc;"><h1>' + service_id.header_model_id.name + '</h1></div>'
            primary_template += '<section class="  row col-lg-12" style="padding:16px;">'
            
            # primary_template += '<t t-set="test" t-value="hr_service_items" />'

            hr_service_grouped_items = {}
            for key, group in groupby(hr_service_items, lambda item: item.field_variant_line_id.id):
                hr_service_grouped_items[key] = list(group)
            keys = sorted(hr_service_grouped_items.keys())
            for key in keys:
                group = hr_service_grouped_items[key]
                if group[0].field_variant_line_id.display_column == 'col_6':
                    # primary_template += "<div class='col-6' style='padding:16px;background-color:#FFFFFF;'>"
                    primary_template += "<div class='col-6' >"
                    primary_template += "<div class='card bg-light mx-3 my-3  p-3  bg-white' style='padding:16px;background-color:#FFFFFF; border-radius: 15px;'>"
                    primary_template += '<div class="mb-2"><h5><strong>' + group[0].field_variant_line_id.description + '</strong></h5></div>'
                    primary_template += '<div class="border border-1 p-3 border-opacity-10" style=" border-radius: 10px;">'

                if group[0].field_variant_line_id.display_column == 'col_12':
                    primary_template += "<div class='col-12'>"
                    primary_template += "<div class='card bg-light mx-3 my-3  p-3  bg-white' style='padding:16px;background-color:#FFFFFF; border-radius: 15px;'>"
                    primary_template += '<div class="mb-2"><h5><strong>' + group[0].field_variant_line_id.description + '</strong></h5></div>'
                    primary_template += '<div class="border border-1 p-3 border-opacity-10" style="border-radius: 10px;">'
                    # primary_template += '<div class="card-header mb-2"><h3>' + group[0].field_variant_line_id.description + '</h3></div>'

                

                for field in group:
                    # find the record value
                    field_domain = []

                    if field.operation_mode:
                        if record_sudo:
                            if field.sudo().field_id.ttype == 'many2one':
                                record_val = record_sudo[eval("'" + field.field_name + "'")].id
                            else:
                                record_val = str(record_sudo[eval("'" + field.field_name + "'")])
                            #primary_template += "<h1>" + str(record_sudo[eval("'" + field.field_name + "'")]) + "=value</h1>"
                    
                        if field.is_required:
                            primary_template += "<div class='form-group mb-2   s_website_form_required' data-type='char' data-name='" + field.field_name + "'>"
                            # primary_template += "<div class='form-group col-4 s_website_form_required' data-type='char' data-name='" + field.field_name + "'>"
                        else:
                            primary_template += "<div class='form-group mb-2 ' data-type='char' data-name='" + field.field_name + "'>"
                            # primary_template += "<div class='form-group col-4' data-type='char' data-name='" + field.field_name + "'>"
                        
                        primary_template += "<label class='s_website_form_label' style='width: 200px' for='" + field.field_name + "'>"
                        primary_template += "<span class='s_website_form_label_content'>" + field.field_label + "</span>"
                        primary_template += "</label>"
                    
                        # Many2one Field
                        if field.field_type == 'many2one':
                            if field.field_model == 'ir.attachment':
                                primary_template += "<input type='file' class='form-control-file mb-2 s_website_form_input' id='" + field.field_name + "' name='" + field.field_name + "' multiple='1' />"
                            else:
                                if field.field_domain:
                                    try:
                                        if 'employee' in field.field_domain:
                                            field_domain = eval(field.field_domain, {"employee": request.env.user.employee_id.id})
                                        elif 'user' in field.field_domain:
                                            field_domain = eval(field.field_domain, {"user": request.env.user.id})
                                        elif 'partner' in field.field_domain:
                                            field_domain = eval(field.field_domain, {"partner": request.env.user.partner_id.id})
                                        else:
                                            field_domain = safe_eval.safe_eval(field.field_domain)
                                    except Exception:
                                        field_domain = []
                                    #e = request.env.user.employee_id.id
                                    #raise ValidationError(eval(field.field_domain, {"employee": request.env.user.employee_id.id}))
                                    #if isinstance(field.field_domain, str):
                                    #    if field.field_domain == 'employee.id':
                                    #        field_domain = [('employee_id','=',request.env.user.employee_id.id)]
                                    #    else:
                                    #        field_domain = safe_eval.safe_eval(field.field_domain)
                                    #field_domain = field_domain.replace("employee.id", "request.env.user.employee_id.id")
                                    #raise ValidationError(_(json.dumps(field.field_domain)))
                                    #field_domain = eval(field.field_domain, {"employee": request.env.user.employee_id.id})
                                m2o_id = request.env[field.field_model].sudo().search(field_domain)
                                # primary_template += "<option value='' " + " selected"  + ">" + "Search for a product </option>"
    
                                if field.ref_populate_field_id:
                                    response_field_name = field.ref_populate_field_id.name
                                    response_field  = hr_service_items.filtered(lambda x:x.field_model == field.ref_populate_field_id.relation)
                                    responce_model = response_field.field_model
                                    model_fields = request.env[field.field_model]._fields
                                    model_fields_dict = dict(model_fields)

                                    model_related_field = None                                
                                    for key, value in model_fields_dict.items():
                                        if value.comodel_name == responce_model:
                                            model_related_field=key

                                    result = model_related_field + '-' + response_field_name
                                
                                    primary_template += "<input type='hidden'  id='join_fields' name='" + result + "' />"
                                    name = field.field_name +"-" + str(service.id)
                                    primary_template += "<select id='" + name + "' name='" + field.field_name + "'class='mb-2 selection-search form-control'" +  " onchange=check_list(this); >"
                                else:
                                    primary_template += "<select id='" + field.field_name + "' name='" + field.field_name + "'class='mb-2 selection-search form-control'>"

                                for m in m2o_id:
                                    primary_template += "<option value='" + str(m.id) + "' " + (" selected" if record_val == m.id else " ") + ">"
                                    #template += "<t t-esc='t" + m.name + "'/>"
                                    primary_template += m.name
                                    primary_template += "</option>"
                                primary_template += "</select>"
                                
                            
                        # Many2many field
                        elif field.field_type == 'many2many':
                            if field.field_domain:
                                try:
                                    if 'employee' in field.field_domain:
                                        field_domain = eval(field.field_domain, {"employee": request.env.user.employee_id.id})
                                    elif 'user' in field.field_domain:
                                        field_domain = eval(field.field_domain, {"user": request.env.user.id})
                                    elif 'partner' in field.field_domain:
                                        field_domain = eval(field.field_domain, {"partner": request.env.user.partner_id.id})
                                    else:
                                        field_domain = safe_eval.safe_eval(field.field_domain)
                                except Exception:
                                    field_domain = []
                            m2m_id = request.env[field.field_model].sudo().search(field_domain) 
                            primary_template += "<select id='" + field.field_name + "' name='" + field.field_name + "'class='form-control mb-2 selection-search' multiple='multiple'>"
                            # primary_template += "<select id='" + field.field_name + "' name='" + field.field_name + "'class='form-control mb-2 selection-search' style='width: 25%' multiple='multiple'>"
                            for m in m2m_id:
                                primary_template += "<option value='" + str(m.id) + "' " + (" selected" if record_val == m.id else " ") + ">"
                                primary_template += m.name
                                primary_template += "</option>"
                            primary_template += "</select>"




                        # Selection field
                        elif field.field_type == 'selection':
                            sel_ids = request.env['ir.model.fields.selection'].sudo().search([('field_id','=',field.field_id.id)])
                            primary_template += "<select id='" + field.field_name + "' name='" + field.field_name + "'class='form-control mb-2' >"
                            for sel in sel_ids:
                                primary_template += "<option value='" + str(sel.value) + "' " + (" selected" if str(record_val) == sel.value else " ") + ">"
                                primary_template += sel.name
                                primary_template += "</option>"
                            primary_template += "</select>"
                    
                        # Date Field
                        elif field.field_type == 'date':
                            primary_template += '<input type="date" class="form-control mb-2 s_website_form_input"' + 'name="' + field.field_name + '"' + ' id="' + field.field_name + '"' + 'value="' + record_val + '"' +  ('required="1"' if field.is_required else '') + ">"
                        elif field.field_type == 'datetime':
                            primary_template += '<input type="datetime-local" class="form-control mb-2 s_website_form_input"' + 'name="' + field.field_name + '"' + ' id="' + field.field_name + '"' + 'value="' + record_val + '"' +  ('required="1"' if field.is_required else '') + ">"
                        elif field.field_type == 'char':
                            primary_template += '<input type="text" class="form-control mb-2 s_website_form_input"' + 'name="' + field.field_name + '"' + ' id="' + field.field_name + '"' + 'value="' + record_val + '"' +  ('required="1"' if field.is_required else '') + ">"
                        elif field.field_type == 'text':
                            primary_template += '<textarea class="form-control mb-2 s_website_form_input"' + 'name="' + field.field_name + '"' + ' id="' + field.field_name + '"' + 'value="' + record_val + '"' +  ('required="1"' if field.is_required else '') + " ></textarea>"
                        elif field.field_type in ('integer','float','monetary'):
                            primary_template += '<input type="number" class="form-control mb-2 s_website_form_input"' + 'name="' + field.field_name + '"' + ' id="' + field.field_name + '"' + 'value="' + record_val + '"' +  ('required="1"' if field.is_required else '') + ">"
                        #elif field.field_type == 'html':
                        #    primary_template += "<input type='text' class='form-control s_website_form_input' name='" + field.field_name + "' id='" + field.field_name + "' value='" + record_val + ("'required=1'" if field.is_required else '') + "'/>"
                        else:
                            primary_template += '<input type="text" class="form-control mb-2 s_website_form_input"' + 'name="' + field.field_name + '"' + ' id="' + field.field_name + '"' + 'value="' + record_val + '"' +  ('required="1"' if field.is_required else '') + ">"

                    
                        primary_template += "</div>"
                primary_template += "</div>"
                primary_template += "</div>"
                primary_template += "</div>"
                        
            # add seperator and button
            primary_template += '<div class="form-group col-12 s_website_form_submit" data-name="Submit Button" style="text-align: right;">'
            primary_template += '<hr class="w-100 mx-auto" style="border-top-width: 1px; border-top-style: solid;"/>'
           
            primary_template += '<div class="row"/>'
            primary_template += '<div class="d-flex flex-row col-6"/>'
            primary_template += '<button type="button" class="btn btn-link p-0 m-0 text-decoration-none" onclick="window.history.back();"  style="text-align: left;">Back</button>'
            
            # <img t-if="record_id.id" src="/de_portal_hr_service/static/icons/previous.png" alt="Previous" t-attf-onclick="action(type = 'previous', {{service.id}} , {{service.header_model_id.id}} , {{record_id.id}} )"/>

            # primary_template += '<button type="button" class="btn btn-primary" onclick="window.history.back();"  style="text-align: left;">Back</button>'
            primary_template += '<span id="s_website_form_result_back"/>'
            primary_template += '</div>'
            primary_template += '<div class="d-flex flex-row-reverse col-6"/>'
            primary_template += '<button type="submit" class="btn btn-primary">Submit</button>'
            # primary_template += '<button type="submit" class="btn btn-primary rounded-circle btn-lg">Submit</button>'
            primary_template += '<span id="s_website_form_result"/>'
            primary_template += '</div>'
            primary_template += '</div>'


            primary_template += "</section>"

        
        # ------------------------------------------
        # -------------Right Section Fields ----------------
        # ------------------------------------------
        """
        for service in service_id:
            for field in hr_service_items:
                field_domain = []
                if record_sudo:
                    if field.field_id.sudo().ttype == 'many2one':
                        record_val = record_sudo[eval("'" + field.field_name + "'")].name
                    else:
                        record_val = str(record_sudo[eval("'" + field.field_name + "'")])
                        
                if field.is_required:
                    extra_template += "<div class='form-group col-12 s_website_form_required' data-type='char' data-name='" + field.field_name + "'>"
                else:
                    extra_template += "<div class='form-group col-12' data-type='char' data-name='" + field.field_name + "'>"
                extra_template += "<label class='s_website_form_label' style='width: 200px' for='" + field.field_name + "'>"
                extra_template += "<span class='s_website_form_label_content'>" + field.field_label + "</span>"
                extra_template += "</label>"
                
                # Many2one Field
                if field.field_type == 'many2one':
                    if field.field_model == 'ir.attachment':
                        extra_template += "<input type='file' class='form-control-file s_website_form_input' id='" + field.field_name + "' name='" + field.field_name + "' multiple='1' />"
                    else:
                        if field.field_domain:
                            field_domain = safe_eval.safe_eval(field.field_domain)
                            
                        m2o_id = request.env[field.field_model].sudo().search(field_domain)
                        
                        extra_template += "<select id='" + field.field_name + "' name='" + field.field_name + "'class='form-control' >"
                        for m in m2o_id:
                            extra_template += "<option value='" + str(m.id) + "' " + (" selected" if record_val == m.name else " ") + ">"
                            #template += "<t t-esc='t" + m.name + "'/>"
                            extra_template += m.name
                            extra_template += "</option>"
                        extra_template += "</select>"
                    
                # Selection field
                elif field.field_type == 'selection':
                    sel_ids = request.env['ir.model.fields.selection'].sudo().search([('field_id','=',field.field_id.id)])
                    extra_template += "<select id='" + field.field_name + "' name='" + field.field_name + "'class='form-control' >"
                    for sel in sel_ids:
                        extra_template += "<option value='" + str(sel.value) + "' " + (" 'selected'" if str(record_val) == sel.value else " ") + ">"
                        extra_template += sel.name
                        extra_template += "</option>"
                    extra_template += "</select>"
                
                # Date Field
                elif field.field_type == 'date':
                    extra_template += '<input type="date" class="form-control s_website_form_input"' + 'name="' + field.field_name + '"' + ' id="' + field.field_name + '"' + 'value="' + record_val + '"' +  ('required="1"' if field.is_required else '') + ">"
                elif field.field_type == 'char':
                    extra_template += '<input type="text" class="form-control s_website_form_input"' + 'name="' + field.field_name + '"' + ' id="' + field.field_name + '"' + 'value="' + record_val + '"' +  ('required="1"' if field.is_required else '') + ">"
                elif field.field_type in ('integer','float','monetary'):
                    extra_template += '<input type="number" class="form-control s_website_form_input"' + 'name="' + field.field_name + '"' + ' id="' + field.field_name + '"' + 'value="' + record_val + '"' +  ('required="1"' if field.is_required else '') + ">"
                #elif field.field_type == 'html':
                #    primary_template += "<input type='text' class='form-control s_website_form_input' name='" + field.field_name + "' id='" + field.field_name + "' value='" + record_val + ("'required=1'" if field.is_required else '') + "'/>"
                else:
                    extra_template += '<input type="text" class="form-control s_website_form_input"' + 'name="' + field.field_name + '"' + ' id="' + field.field_name + '"' + 'value="' + record_val + '"' +  ('required="1"' if field.is_required else '') + ">"
                
                extra_template += "</div>"
        """
            
        currency_ids = request.env['res.currency'].sudo().search([('active','=',True)])
        return {
            'currency_ids': currency_ids,
            'template_primary_fields': primary_template,
            'template_extra_fields': extra_template,
            'service_id': service_id,
            'record_id': record_id,
            'model_id': model_id,
            'edit_mode': edit_mode or 0,
        }
    
    @http.route(['/my/model/record/<int:service_id>/<int:model_id>/<int:record_id>/<int:edit_mode>'
                ], type='http', auth="user", website=True)        
    def portal_hr_service_record(self, service_id=False, model_id=False, record_id=False, edit_mode=False, **kw):
        return request.render("de_portal_hr_service.portal_service_record_form", self._prepare_service_record_page(service_id, model_id, record_id, edit_mode))
        
    # @http.route(['/my/model/record/next/<int:service_id>/<int:model_id>/<int:record_id>'
    @http.route(['/my/model/record/next/prev'], type='http', method=['POST'], auth="user", website=True,
                csrf=False)
    def portal_hr_service_record_next(self,**kw):
        try:
            btn = kw.get('btn')
            service = kw.get('service_id')
            model = kw.get('model_id')
            record = kw.get('record_id')
            service_id = request.env['hr.service'].sudo().search([('id','=',int(service))],limit=1)
            line_item = request.env['hr.service.record.line'].search([('hr_service_id','=',service_id.id),('line_model_id','=',int(model))],limit=1)
            model = request.env['ir.model'].sudo().search([('id','=',int(model))],limit=1)
            
            message_partner_ids = request.env['ir.model.fields'].sudo().search([('name','=','message_partner_ids'),('model','=',service_id.header_model_id.model)],limit=1)
            employee_id = request.env['ir.model.fields'].sudo().search([('name','=','employee_id'),('model','=',service_id.header_model_id.model)],limit=1)
            partner_id = request.env['ir.model.fields'].sudo().search([('name','=','partner_id'),('model','=',service_id.header_model_id.model)],limit=1)


            if service_id.filter_field_id:
                domain = [(service_id.filter_field_id.name, 'child_of', [request.env.user.partner_id.id]),
                (service_id.filter_field_id.name, '=', [request.env.user.partner_id.id])]
   
            if service_id.filter_domain:
                domain = safe_eval.safe_eval(service_id.filter_domain) + domain
            model_records = request.env[service_id.header_model_id.model].sudo().search(domain).ids
            rec_id = None
            if btn == 'next':
                rec_id = next(dropwhile(lambda x: x <= int(record), sorted(model_records)), None)
                if not rec_id:
                    rec_id = min(model_records)

            if btn == 'previous':
                sorted_list = sorted(model_records)
                index = sorted_list.index(int(record))
                if index > 0:
                    rec_id = sorted_list[index - 1]
                elif index == 0:
                    rec_id = sorted_list[-1]
            record_sudo = request.env[service_id.header_model_id.model].sudo().search([('id','=',int(rec_id))],limit=1)
      
            data = {
                'status_is': "Success",
                'next_record': record_sudo.id,
            }

        except Exception as e:
            data = {
                'status_is': "Error",
                'message': e.args[0],
                'color': '#FF0000'
            }
        data = json.dumps(data)
        return data   
            
        


        # return request.render("de_portal_hr_service.portal_service_record_form", self._prepare_service_record_page(service_id, model_id, record_id, edit_mode))
        
    @http.route(['/my/model/record/prev/<int:service_id>/<int:model_id>/<int:record_id>'
                ], type='http', auth="user", website=True)        
    def portal_hr_service_record_previous(self, service_id=False, model_id=False, record_id=False, edit_mode=False, **kw):
        return request.render("de_portal_hr_service.portal_service_record_form", self._prepare_service_record_page(service_id, model_id, record_id, edit_mode))
        
    
    @http.route('/my/model/record/submit', website=True, page=True, auth='public', csrf=False)
    def hr_service_record_submit(self, **kw):
        
        service_id = request.env['hr.service'].sudo().search([('id','=',(kw.get('service_id')))],limit=1)
        model = request.env['ir.model'].sudo().search([('id','=',(kw.get('model_id')))],limit=1)
        # request.httprequest.form.getlist('tag_ids')
        record_sudo = False
        parent_record_sudo = False
        record = False
        
        res_name = False
        service_items = False
        
        model_id = (kw.get('model_id'))
        record_id = (kw.get('record_id'))
        edit_mode = (kw.get('edit_mode'))
        
        if model_id and record_id:
            model = request.env['ir.model'].search([('id','=',model_id)],limit=1)
            rs = request.env[model.model].search([('id','=',record_id)],limit=1)
        
        field_val = False
        
        line_item = request.env['hr.service.record.line'].search([('hr_service_id','=',service_id.id),('line_model_id','=',int(model_id))],limit=1)


        if service_id.header_model_id.id == int(model_id):
            service_items = service_id.hr_service_items
            if edit_mode == '1' or edit_mode == 1:
                record_sudo = request.env[service_id.header_model_id.model].sudo().search([('id','=',int(record_id))],limit=1)
                res_name = record_sudo.name
        elif line_item.line_model_id: #service_id.line_model_id.id == int(model_id):
            service_items = line_item.hr_service_record_line_items #line_model_id.hr_service_record_line_items #.hr_service_items_line
            if edit_mode == '1' or edit_mode == 1:
                record_sudo = request.env[line_item.line_model_id.model].sudo().search([('id','=',int(record_id))],limit=1)
                res_name = record_sudo.name
        
        user_id = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))],limit=1)
        
        vals = {}
        
        for field in service_items.filtered(lambda r: r.field_model):
            if field.field_model == 'res.users':
                vals.update({
                    field.field_name: user_id.id,
                })
            elif field.field_model == 'hr.employee':
                vals.update({
                    field.field_name: user_id.employee_id.id,
                })
            elif field.field_model == 'res.partner':
                vals.update({
                    field.field_name: user_id.partner_id.id,
                })
        
        # for field in service_items.filtered(lambda r: r.auto_populate):
        #     if field.auto_populate == 'user':
        #         vals.update({
        #             field.field_name: user_id.id,
        #         })
        #     elif field.auto_populate == 'employee':
        #         vals.update({
        #             field.field_name: user_id.employee_id.id,
        #         })
        #     elif field.auto_populate == 'partner':
        #         vals.update({
        #             field.field_name: user_id.partner_id.id,
        #         })
        
        for field in service_items:
            if kw.get(field.field_name):
                field_val = kw.get(field.field_name)
                #vals.update({
                #    'prepayment_type_id': 1, #m2o_id.id,
                #})
                #vals.update({
                #    'amount': 100, #m2o_id.id,
                #})
                if field.field_type == 'many2one':
                    if field.field_model == 'ir.attachment':
                        data_file_name = kw.get(field.field_name).filename
                        data_file = kw.get(field.field_name)
                        attachment_id = request.env['ir.attachment'].sudo().create({
                            'name': data_file_name,
                            'type': 'binary',
                            'datas': base64.b64encode(data_file.read()),
                            'res_model': model.model,
                            'res_id': record_id,
                            'res_name': res_name,
                        })
                        vals.update({
                            field.field_name: attachment_id.id,
                        })
                    else:
                        #m2o_id = request.env[field.field_model].sudo().search([('id','=',kw.get(field.field_name))])
                        
                        m2o_id = request.env[field.field_model].sudo().search([('id','=',int(field_val))],limit=1)
                        vals.update({
                            field.field_name: m2o_id.id,
                        })
                elif field.field_type == 'many2many':
                    field_val = request.httprequest.form.getlist(field.field_name)
                    m2m_ids = request.env[field.field_model].sudo().search([('id','in',field_val)])
                    vals.update({
                        # field.field_name: [(6,0,m2m_ids.ids)],
                        field.field_name: m2m_ids.ids,
                    })
                elif field.field_type == 'float':
                    vals.update({
                        field.field_name: float(kw.get(field.field_name))
                    })
                else:
                    vals.update({
                        field.field_name: kw.get(field.field_name)
                    })
            
        for field in service_items.filtered(lambda r: r.ref_field_id):
            if field.ref_field_id.ttype == 'many2one':
                ref_record_id = request.env[field.ref_field_id.relation].sudo().search([('id','=',int(kw.get(field.ref_field_id.name)))],limit=1)
                rel_field_id = request.env['ir.model.fields'].sudo().search([('model_id.model','=',field.ref_field_id.relation),('relation','=',field.field_model)],limit=1)
                vals.update({
                        field.field_name: ref_record_id[eval("'" + rel_field_id.name + "'")].id
                    })
            else:
                vals.update({
                        field.field_name: kw.get(field.ref_field_id.name)
                    })
        
        #raise ValidationError(_(str(ref_field_id)+str(rel_field_id)+str(safe_eval.safe_eval(str(ref_field_id)+'.'+str(rel_field_id.name)+'.id')) ))
        #raise ValidationError(str(ref_record_id[eval("'" + rel_field_id.name + "'")].id))
        if service_id.header_model_id.id == int(model_id):
            if edit_mode == '0' or edit_mode == 0 or not edit_mode:
                record_sudo = request.env[service_id.header_model_id.model].sudo().create(vals)
            else:
                record_sudo.sudo().write(vals)
            record = record_sudo
                
        elif line_item.line_model_id.id == int(model_id):
            if edit_mode == '0' or edit_mode == 0 or not edit_mode:
                parent_record_sudo = request.env[service_id.header_model_id.model].sudo().search([('id','=',int(record_id))],limit=1)
                #parent_record_sudo = request.env[service_id.line_model_id.model].sudo().search([('id','=',record_sudo[eval("'" + service_id.parent_relational_field_id.name + "'")].id)],limit=1)
                vals.update({
                    line_item.sudo().parent_relational_field_id.name: int(record_id), #parent_record_sudo.id
                })
                record_sudo = request.env[line_item.line_model_id.model].sudo().create(vals)
                record = parent_record_sudo
            else:
                record = record_sudo[eval("'" + line_item.parent_relational_field_id.sudo().name + "'")]
                record_sudo.sudo().write(vals)
        
        #raise UserError(str(record_id))
        #elif kw.get('mode') == '1':
        #    if record_sudo:
        #        record_sudo.sudo().write(vals)
        #        if parent_record_id:
        #            parent_record_id = record_sudo.id
        #        else:
        #            record_id = record_sudo.id
        
            
        return request.redirect('/my/model/record/%s/%s/%s' % (service_id.id,service_id.header_model_id.id, record.id))
    
    #delete record
    @http.route(['/my/model/record/<int:service_id>/<int:model_id>/<int:record_id>/delete'
                ], type='http', auth="user", website=True)        
    def portal_hr_service_record_delete(self, service_id=False, model_id=False, record_id=False, **kw):
        
        service_id = request.env['hr.service'].sudo().search([('id','=',int(service_id))],limit=1)
        record_sudo = False
        record = False
        line_item = request.env['hr.service.record.line'].search([('hr_service_id','=',service_id.id),('line_model_id','=',int(model_id))],limit=1)

        if service_id.header_model_id.id == int(model_id):
            record_sudo = request.env[service_id.header_model_id.model].sudo().search([('id','=',int(record_id))],limit=1)
            record = request.env[service_id.header_model_id.model].sudo().search([('id','=',int(record_id))],limit=1)
        elif line_item.line_model_id.id == int(model_id):
            record_sudo = request.env[line_item.line_model_id.model].sudo().search([('id','=',int(record_id))],limit=1)
            record = record_sudo[eval("'" + line_item.parent_relational_field_id.sudo().name + "'")]
                
        record_sudo.sudo().unlink()
        return request.redirect('/my/model/record/%s/%s/%s' % (service_id.id,model_id, record.id))

    #Download import sample record
    @http.route(['/download/sample/import/record/<int:service_id>/<int:record_line_id>'
                ], type='http', auth="user", website=True)        
    def download_import_sample_record(self, service_id=False, record_line_id=False, **kw):
        service_id = request.env['hr.service'].sudo().search([('id','=',int(service_id))],limit=1)
        line_item = request.env['hr.service.record.line'].search([('hr_service_id','=',service_id.id),('id','=',int(record_line_id))],limit=1)
        status, content, filename, mimetype, filehash = request.env['ir.http'].sudo()._binary_record_content(line_item,
                                                                                                     field='file_attachment')
        status, headers, content = request.env['ir.http'].sudo()._binary_set_headers(status, content, filename, mimetype,
                                                                             unique=False, filehash=filehash,
                                                                             download=True)
        if status != 200:
            return request.env['ir.http'].sudo()._response_by_status(status, headers, content)
        else:
            content_base64 = base64.b64decode(content)
            headers.append(('Content-Length', len(content_base64)))
            response = request.make_response(content_base64, headers)
        return response

    @http.route(['/items/document'], type='http', method=['POST'], auth="user", website=True,
                csrf=False)
    def itemsDocument(self, **kw):
        try:
            import_type = kw.get('import_type')
            service = kw.get('service')
            model = kw.get('model')
            record = kw.get('record')
            service_id = request.env['hr.service'].sudo().search([('id','=',int(service))],limit=1)
            line_item = request.env['hr.service.record.line'].search([('hr_service_id','=',service_id.id),('line_model_id','=',int(model))],limit=1)
            model = request.env['ir.model'].sudo().search([('id','=',int(model))],limit=1)
            record_sudo = request.env[service_id.header_model_id.model].sudo().search([('id','=',int(record))],limit=1)

            if kw.get('file'):
                file = base64.b64encode(kw.get('file').read())
                result = import_data(self_ref = request,model = model,record_sudo=record_sudo,import_type = import_type,file=file,line_item = line_item,service_id=service_id)

            file_detail = kw.get('file')
            file_name = file_detail.filename
            attachment = request.env['ir.attachment'].sudo().create({
                'name': file_name or '',
                'datas': file,
                'res_model': record_sudo._name,
                'res_name': record_sudo._name,
                'res_id': record_sudo.id,
            })

            message = 'File %s' % file_name +  ' imported with total %s' % result + ' records'
            record_sudo.message_post(body=message)
            data = {
                'status_is': "Success",
                'counter': result,
            }

        except Exception as e:
            print(e)
            data = {
                'status_is': "Error",
                'message': e.args[0],
                'color': '#FF0000'
            }
        data = json.dumps(data)
        return data   
            
