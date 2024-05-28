# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from operator import itemgetter
from odoo.addons.de_portal_hr_service.common import (import_data)

from markupsafe import Markup

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, UserError, ValidationError

from odoo import http
from odoo.http import request, Response

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
import datetime

#from odoo.addons.website.controllers import form
import ast

import logging

_logger = logging.getLogger(__name__)


import json

class CustomerPortal(portal.CustomerPortal):
    """
    @http.route('/dynamic_filter', type='http', auth="user", methods=['GET'])
    def dynamic_filter(self, model, field, search_fields, domain, label_fields, q):
        Model = request.env[model]
        domain = ast.literal_eval(domain) if domain else []
        search_domain = [('name', 'ilike', q)]
        for search_field in search_fields.split(','):
            search_domain.append((search_field, 'ilike', q))
        domain = ['|' * (len(search_domain) - 1)] + search_domain + domain
        records = Model.search(domain, limit=10)
        
        label_fields_list = label_fields.split(',')
        results = []
        for record in records:
            label = ' - '.join([str(getattr(record, f)) for f in label_fields_list])
            results.append({'id': record.id, 'text': label})

        return json.dumps(results)
    """

    """
    @http.route('/dynamic_search', type='http', auth="user", methods=['GET'])
    def dynamic_search(self, **kwargs):
        q = kwargs.get('q', '')
        model = kwargs.get('model', '')
        field = kwargs.get('field', '')
        page = int(kwargs.get('page', 1))
        
        limit = 20
        offset = (page - 1) * limit
        domain = [(field, 'ilike', q)]
        
        records = request.env[model].sudo().search(domain, limit=limit, offset=offset)
        items = [{'id': record.id, 'text': getattr(record, field)} for record in records]
        
        return Response(json.dumps({'items': items}), content_type='application/json;charset=utf-8', status=200)
    """
    @http.route('/dynamic_search', type='http', auth="user", methods=['GET'])
    def dynamic_search(self, **kwargs):
        q = kwargs.get('q', '')
        model = kwargs.get('model', '')
        field = kwargs.get('field', '')
        search_fields = kwargs.get('search_fields', '').split(',')
        domain = kwargs.get('domain', '[]')
        label_fields = kwargs.get('label_fields', '').split(',')
        page = int(kwargs.get('page', 1))
        
        limit = 20
        offset = (page - 1) * limit

        # Extend the domain to search across multiple fields
        search_domain = ['|'] * (len(search_fields) - 1)
        for search_field in search_fields:
            search_domain.append((search_field, 'ilike', q))
        
        # Log the received domain
        _logger.info("Received domain: %s", domain)

        # Check if domain is not empty
        if not domain or domain == "":
            evaluated_domain = []
        else:
            # Explicitly parse the domain string
            try:
                evaluated_domain = ast.literal_eval(domain)
                if not isinstance(evaluated_domain, list):
                    raise ValueError("Domain is not a list")
            except Exception as e:
                _logger.error("Error parsing domain: %s", str(e))
                return Response(json.dumps({'error': 'Invalid domain format'}), content_type='application/json;charset=utf-8', status=400)

        combined_domain = evaluated_domain + search_domain

    

        records = request.env[model].sudo().search(combined_domain, limit=limit, offset=offset)
        
        # Concatenate fields for display
        items = [{'id': record.id, 'text': ' '.join([str(getattr(record, lbl_field)) for lbl_field in label_fields])} for record in records]

        
        return Response(json.dumps({'items': items}), content_type='application/json;charset=utf-8', status=200)

    @http.route('/custom/get_form_vals', type='http', auth='public', website=True)
    def get_form_vals(self, **kwargs):

        src_field_name = request.form.get('src_field_name')
        src_field_value = request.form.get('src_field_value')
        model_id = kwargs.get('model_id')

        response_data = {}
        if src_field_name in field_values:
            response_data[src_field_name] = field_values[src_field_name]
        
        # Assuming we want to update a select field
        response_data['selectField'] = field_values['selectField']
    
        return jsonify(response_data)


        
    @http.route('/custom/get_field_vals', type='http', auth='public', website=True)
    def get_field_vals(self, **kwargs):

        field_name = kwargs.get('src_field_name')
        field_value = kwargs.get('src_field_value')
        target_field_name = kwargs.get('target_field_name', 'uom_id')  # default to 'uom_id' if not provided
        #model = kwargs.get('model_id')
        
        model = request.env['ir.model'].search([('id','=',kwargs.get('model_id'))],limit=1)

        # 1. Get the source field id object. e.g product_id
        # 2. Get the source record. e.g product = 'Communication'
        src_field_id = request.env['ir.model.fields'].search([('model_id','=',model.id),('name','=',field_name)],limit=1)
        src_record = request.env[src_field_id.relation].sudo().search([('id','=',field_value)],limit=1)
        
        target_field_id = request.env['ir.model.fields'].search([('model_id','=',model.id),('name','=',target_field_name)],limit=1)
        src_target_field_id = request.env['ir.model.fields'].sudo().search([('model_id.model','=',src_field_id.relation),('relation','=',target_field_id.relation)],limit=1)

        if src_target_field_id.ttype == 'many2one':
            # This code will execute if source-target_field data type is many2one
            # 1. Get the target field value from the source record. e.g km
            # 2. Get the record from the target model on target field value. e.g id=7, name=km
            src_target_field_record = src_record[eval("'" + src_target_field_id.name + "'")]
            target_record = request.env[target_field_id.relation].sudo().search([('id','=',src_target_field_record.id)],limit=1)
            options = {target_record.id: target_record.name}
        elif src_target_field_id.ttype == 'one2many':
            # This code will execute if source-target_field data type is one2many
            target_record = src_record[eval("'" + src_target_field_id.name + "'")]
            options = {t.id: t.name for t in target_record}
        else:
            options = {}
        
        # Check if the record exists
        if not src_record.exists():
            return Response("Record not found", status=400)

        if target_record or len(target_record):
            return json.dumps(options)
            #return Response(target_record.name, status=400)
            #return json.dumps(options)
        else:
            options = {}
            return json.dumps(options)
            #return Response("Invalid field or record not found", status=400)
            #options = {record_id: record_val}
            #return json.dumps(options)
            #return Response(f"{record_id}: {record_val}")

        print("Starting dynamic_search...")
        print("Query:", q)
        print("Model:", model)
        print("Field:", field)
        print("Search Fields:", search_fields)
        print("Domain:", combined_domain)

    # ===========================================================
    # =================== Service Page ==========================
    # ===========================================================
    def _prepare_service_record_page(self, service_id, model_id, record_id, edit_mode, js_code):
        service = request.env['hr.service'].sudo().browse(service_id)
        line_item = request.env['hr.service.record.line'].search([
            ('hr_service_id', '=', service.id),
            ('line_model_id', '=', int(model_id))
        ], limit=1)
    
        hr_service_items, record_sudo = self._get_hr_service_items(service, model_id, record_id, line_item, edit_mode)
    
        primary_template = self._generate_dynamic_form(service, hr_service_items, record_sudo)
    
        currency_ids = request.env['res.currency'].sudo().search([('active', '=', True)])
        js_code = self._generate_js_code()
    
        return {
            'currency_ids': currency_ids,
            'template_primary_fields': primary_template,
            'template_extra_fields': '',
            'service_id': service,
            'record_id': record_id,
            'model_id': model_id,
            'edit_mode': edit_mode,
            'js_code': js_code,
        }
    
    def _get_hr_service_items(self, service, model_id, record_id, line_item, edit_mode):
        record_sudo = request.env[service.header_model_id.model]
        if service.header_model_id.id == int(model_id):
            hr_service_items = service.hr_service_items.filtered(lambda x: x.operation_mode)
            if edit_mode in ('1', 1):
                record_sudo = request.env[service.header_model_id.model].sudo().browse(record_id)
        elif line_item:
            hr_service_items = line_item.hr_service_record_line_items.filtered(lambda x: x.operation_mode)
            if edit_mode in ('1', 1):
                record_sudo = request.env[line_item.line_model_id.model].sudo().browse(record_id)
        else:
            hr_service_items = record_sudo = False
        return hr_service_items, record_sudo
    
    def _generate_dynamic_form(self, service, hr_service_items, record_sudo):
        primary_template = self._get_base_template(service)
    
        hr_service_grouped_items = self._group_service_items(service)
        for key, group in sorted(hr_service_grouped_items.items()):
            primary_template += self._get_column_template(group)
    
            for field in hr_service_items.filtered(lambda x: x.field_variant_line_id.id == key.id):
                record_val, required, required_label = self._get_field_properties(field, record_sudo)
    
                primary_template += self._generate_field_template(field, record_val, required, required_label)
    
            primary_template += "</div></div></div>"
    
        primary_template += self._get_footer_template()
    
        return primary_template
    
    def _get_base_template(self, service):
        return '''
        <link href="/de_portal_hr_service/static/src/select_two.css" rel="stylesheet" />
        <script type="text/javascript" src="/de_portal_hr_service/static/src/js/jquery.js"></script>
        <script type="text/javascript" src="/de_portal_hr_service/static/src/js/select_two.js"></script>
        <script type="text/javascript" src="/de_portal_hr_service/static/src/js/dynamic_form.js"></script>
        <link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-beta.1/dist/css/select2.min.css" rel="stylesheet" />
        <script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-beta.1/dist/js/select2.min.js"></script>
        <nav class="navbar navbar-light navbar-expand-lg border py-0 mb-2 o_portal_navbar mt-3 rounded">
            <ol class="o_portal_submenu breadcrumb mb-0 py-2 flex-grow-1 row">
                <li class="breadcrumb-item ml-1">
                    <a href="/my/home" aria-label="Home" title="Home"><i class="fa fa-home"></i></a>
                </li>
                <li class="breadcrumb-item active">{header_model_name}</li>
            </ol>
        </nav>
        <div class="row" style="">
        '''.format(header_model_name=service.header_model_id.name)
    
    def _group_service_items(self, service):
        hr_service_grouped_items = {}
        for key, group in groupby(service.field_variant_id.field_variant_line_ids):
            hr_service_grouped_items[key] = list(group)
        return hr_service_grouped_items
    
    def _get_column_template(self, group):
        if group[0].display_column == 'col_6':
            return '''
            <div class='col-6'>
                <div class='p-3 h-100 bg-white'>
                    {header}
                    <div style="border-radius: 10px;">
            '''.format(header=self._get_column_header(group))
        elif group[0].display_column == 'col_12':
            return '''
            <div class='col-12'>
                <div class='p-3 h-100 bg-white'>
                    {header}
                    <div style="border-radius: 10px;">
            '''.format(header=self._get_column_header(group))
        return ''
    
    def _get_column_header(self, group):
        if group[0].description:
            return '''
            <div class="mb-2">
                <h5 class="text-uppercase text-o-color-1">{description}</h5>
                <hr class="w-100 mx-auto" />
            </div>
            '''.format(description=group[0].description)
        return '<div class="mb-2"></div>'
    
    def _get_field_properties(self, field, record_sudo):
        record_val = ''
        if record_sudo:
            record_val = str(record_sudo[field.field_name]) if field.field_type != 'many2one' else record_sudo[field.field_name].id
        required = '1' if field.is_required else ''
        required_label = '*' if field.is_required else ''
        return record_val, required, required_label
    
    def _generate_field_template(self, field, record_val, required, required_label):
        template = '''
        <div class='form-group mb-2 {required_class}' data-type='char' data-name='{field_name}'>
            <label class='s_website_form_label' style='width: 200px' for='{field_name}'>
                <span class='s_website_form_label_content'>{field_label}{required_label}</span>
            </label>
        '''.format(
            required_class='s_website_form_required' if required else '',
            field_name=field.field_name,
            field_label=field.field_label,
            required_label=required_label
        )
    
        if field.field_type == 'many2one':
            template += self._generate_many2one_field(field, record_val, required)
        elif field.field_type == 'many2many':
            template += self._generate_many2many_field(field, record_val, required)
        elif field.field_type == 'selection':
            template += self._generate_selection_field(field, record_val, required)
        elif field.field_type == 'date':
            template += '<input type="date" class="form-control mb-2 s_website_form_input" name="{field_name}" id="{field_name}" value="{record_val}" {required}>'.format(
                field_name=field.field_name, record_val=record_val, required='required="1"' if required else ''
            )
        elif field.field_type == 'datetime':
            template += self._generate_datetime_field(field, record_val, required)
        elif field.field_type in ('char1', 'text1', 'integer', 'float', 'monetary'):
            template += '<input type="{input_type}" class="form-control mb-2 s_website_form_input" name="{field_name}" id="{field_name}" value="{record_val}" {required}>'.format(
                input_type='number' if field.field_type in ('integer', 'float', 'monetary') else 'text',
                field_name=field.field_name, record_val=record_val, required='required="1"' if required else ''
            )
        else:
            template += '''
            <input type="text" class="form-control mb-2 s_website_form_input" name="{field_name}" id="{field_name}" onchange="filter_field_vals(this)" value="{record_val}" {required}>
            '''.format(field_name=field.field_name, record_val=record_val, required='required="1"' if required else '')
    
        template += "</div>"
        return template
    
    def _generate_many2one_field(self, field, record_val, required):
        field_domain = self._get_field_domain(field)
        m2o_id = request.env[field.field_model].sudo().search(field_domain)
        domain_filter = str(field_domain).replace("'", "&#39;") if field_domain else ""
    
        if field.field_model == 'ir.attachment':
            return '''
            <input type='file' class='form-control-file mb-2 s_website_form_input' id='{field_name}' name='{field_name}' multiple='1' />
            '''.format(field_name=field.field_name)
    
        ref_populate = " onchange='filter_field_vals(this, {ref_populate_field})'".format(ref_populate_field=field.ref_populate_field_id.name) if field.ref_populate_field_id else ""
    
        search_fields = ','.join(field.search_fields_ids.mapped('name'))
        label_fields = ','.join(field.label_fields_ids.mapped('name'))
    
        select_tag = '''
        <select id='{field_name}' name='{field_name}' {required} data-model='{field_model}' data-field='name' data-search-fields='{search_fields}' data-label-fields='{label_fields}' data-domain='{domain_filter}' class='mb-2 select2-dynamic selection-search form-control'{ref_populate}>
            <option value=''>Select</option>
        '''.format(
            field_name=field.field_name, required='required="1"' if required else '',
            field_model=field.field_model, search_fields=search_fields, label_fields=label_fields,
            domain_filter=domain_filter, ref_populate=ref_populate
        )
    
        for rec in m2o_id:
            selected = 'selected="selected"' if rec.id == record_val else ''
            # Combine label fields
            combined_label = ' '.join([str(rec[label]) for label in field.label_fields_ids.mapped('name') if rec[label]])
            select_tag += "<option value='{id}' {selected}>{name}</option>".format(id=rec.id, selected=selected, name=combined_label)
    
        select_tag += "</select>"
        return select_tag


    
    def _generate_many2many_field(self, field, record_val, required):
        field_domain = self._get_field_domain(field)
        m2m_ids = request.env[field.field_model].sudo().search(field_domain)
        domain_filter = str(field_domain).replace("'", "&#39;") if field_domain else ""
    
        selected_ids = record_val if record_val else []
    
        m2m_template = '''
        <select id='{field_name}' name='{field_name}' {required} data-model='{field_model}' data-field='name' data-search-fields='{search_fields}' data-label-fields='{label_fields}' data-domain='{domain_filter}' class='select2-dynamic-multiple selection-search form-control' multiple>
        '''.format(
            field_name=field.field_name, required='required="1"' if required else '',
            field_model=field.field_model, search_fields=field.search_fields_ids.ids, label_fields=field.label_fields_ids,
            domain_filter=domain_filter
        )
    
        for rec in m2m_ids:
            selected = 'selected="selected"' if rec.id in selected_ids else ''
            m2m_template += "<option value='{id}' {selected}>{name}</option>".format(id=rec.id, selected=selected, name=rec.name)
    
        m2m_template += "</select>"
        return m2m_template
    
    def _generate_selection_field(self, field, record_val, required):
        selection_template = '''
        <select id='{field_name}' name='{field_name}' {required} class='selection-search form-control mb-2'>
        '''.format(field_name=field.field_name, required='required="1"' if required else '')
    
        for val, label in eval(field.field_selection):
            selected = 'selected="selected"' if val == record_val else ''
            selection_template += "<option value='{val}' {selected}>{label}</option>".format(val=val, selected=selected, label=label)
    
        selection_template += "</select>"
        return selection_template
    
    def _generate_datetime_field(self, field, record_val, required):
        return '''
        <input type="datetime-local" class="form-control mb-2 s_website_form_input" name="{field_name}" id="{field_name}" value="{record_val}" {required}>
        '''.format(field_name=field.field_name, record_val=record_val, required='required="1"' if required else '')
    
    def _get_footer_template(self):
        return '''
        </div></div>
        <div class="col-12">
            <div class="bg-white rounded">
                <div class="row m-0">
                    <div class="col-12">
                        <div class="bg-light p-3 mt-3 rounded">
                            <div class="text-right">
                                <button type="submit" class="btn btn-primary">Save</button>
                                <a href="#" class="btn btn-secondary">Cancel</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        '''
    
    def _get_field_domain(self, field):
        if field.field_domain:
            return eval(field.field_domain)
        return []
    
    def _generate_js_code(self):
        return '''
        <script type="text/javascript">
            $(document).ready(function() {
                $('.select2-dynamic').select2({
                    theme: 'bootstrap4',
                    placeholder: 'Select an option',
                    allowClear: true,
                });
            });
    
            function filter_field_vals(formId) {
                // Function implementation
            }
    
        </script>
        '''

    # End Service Record Page

    
    def _prepare_service_record_page1(self,service_id, model_id, record_id, edit_mode, js_code):
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
        
        required = '0'
        required_label = ''
        
        data_pre = stDate = dat_time = ''
        
        line_item = request.env['hr.service.record.line'].search([('hr_service_id','=',service_id.id),('line_model_id','=',int(model_id))],limit=1)
        
        if service_id.header_model_id.id == int(model_id):
            #record_id = request.env[service_id.header_model_id.model].sudo().search([('id','=',int(rec_id))],limit=1).id
            hr_service_items = service_id.hr_service_items.filtered(lambda x: x.operation_mode)
            if edit_mode == '1' or edit_mode == 1:
                record_sudo = request.env[service_id.header_model_id.model].sudo().search([('id','=',record_id)],limit=1)
                        
        elif line_item:
            #record_id = request.env[service_id.line_model_id.model].sudo().search([('id','=',int(rec_id))],limit=1).id
            #hr_service_items = line_model_id.hr_service_record_line_items #service_id.hr_service_items_line
            hr_service_items = line_item.hr_service_record_line_items.filtered(lambda x: x.operation_mode)
            if edit_mode == '1' or edit_mode == 1:
                record_sudo = request.env[line_item.line_model_id.model].sudo().search([('id','=',record_id)],limit=1)            

                
        
        # ----------------------------------------------------
        # ------------- Generate Dynamic Form ----------------
        # ----------------------------------------------------
        for service in service_id:
            primary_template += '<link href="/de_portal_hr_service/static/src/select_two.css" rel="stylesheet" />'
            primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/jquery.js"></script>'
            primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/select_two.js"></script>'
            primary_template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/dynamic_form.js"></script>'

            # libraries used for dynamic search 
            primary_template += '<link href="https://cdn.jsdelivr.net/npm/select2@4.1.0-beta.1/dist/css/select2.min.css" rel="stylesheet" />'
            primary_template += '<script src="https://cdn.jsdelivr.net/npm/select2@4.1.0-beta.1/dist/js/select2.min.js"></script>'
            
        
            primary_template += '<nav class="navbar navbar-light navbar-expand-lg border py-0 mb-2 o_portal_navbar  mt-3 rounded">'
            primary_template += '<ol class="o_portal_submenu breadcrumb mb-0 py-2 flex-grow-1 row">'
            primary_template += '<li class="breadcrumb-item ml-1" data-oe-model="ir.ui.view" data-oe-id="1049" data-oe-field="arch" data-oe-xpath="/t[1]/ol[1]/li[1]"><a href="/my/home" aria-label="Home" title="Home"><i class="fa fa-home"></i></a></li>'
            primary_template += '<li class="breadcrumb-item active ">' + service_id.header_model_id.name + '</li>'
            primary_template += '</ol>'
            primary_template += '</nav>'
            
            primary_template += '<div class="row" style="">'
            
            
            hr_service_grouped_items = {}
            for key, group in groupby(service_id.field_variant_id.field_variant_line_ids):
                hr_service_grouped_items[key] = list(group)
            keys = sorted(hr_service_grouped_items.keys())
            
            for key in keys:
                group = hr_service_grouped_items[key]
                if group[0].display_column == 'col_6':
                    # primary_template += "<div class='col-6' style='padding:16px;background-color:#FFFFFF;'>"
                    primary_template += "<div class='col-6 ' >"
                    primary_template += "<div class='p-3 h-100 bg-white' style=''>"
                    if group[0].description:
                        primary_template += '<div class="mb-2"><h5 class="text-uppercase text-o-color-1">' + group[0].description + '</h5>'
                        primary_template += '<hr class="w-100 mx-auto" />'
                        primary_template += '</div>'
                    else:
                        primary_template += '<div class="mb-2"></div>'
                        
                    primary_template += '<div class="" style=" border-radius: 10px;">'

                if group[0].display_column == 'col_12':
                    primary_template += "<div class='col-12'>"
                    primary_template += "<div class='p-3 h-100 bg-white' style=''>"
                    if group[0].description:
                        primary_template += '<div class="mb-2"><h5 class="text-uppercase text-o-color-1">' + group[0].description + '</h5>'
                    else:
                        primary_template += '<div class="mb-2"></div>'
                        
                    primary_template += '<div class="" style="border-radius: 10px;">'
                
                for field in hr_service_items.filtered(lambda x:x.field_variant_line_id.id == key.id):
                    # find the record value
                    field_domain = []

                    #Search and label fields 
                    if field.field_id.relation:
                        related_model_name = field.field_id.relation
                        Model = request.env[related_model_name]
                        default_field = 'name' if 'name' in Model._fields else 'id'
                        # Assuming you've already fetched the field record in some manner
                        search_fields = [f.name for f in field.search_fields_ids] or [default_field]
                        label_fields = [f.name for f in field.label_fields_ids] or [default_field]
                    else:
                        search_fields = ''
                        label_fields = ''
                    #search_fields = ','.join([f.name for f in field.search_fields_ids])
                    #label_fields = ','.join([f.name for f in field.label_fields_ids])

                    # check the domain
                    domain_filter = str(field.field_domain).replace("'", "&#39;") if field.field_domain else ""

                    
                    if field.is_required:
                        required = '1'
                        required_label = '*'
                    else:
                        required = ''
                        required_label = ''

                    if field.operation_mode:
                        if record_sudo:
                            if field.sudo().field_id.ttype == 'many2one':
                                record_val = record_sudo[eval("'" + field.field_name + "'")].id
                            else:
                                record_val = str(record_sudo[eval("'" + field.field_name + "'")])
                            #primary_template += "<h1>" + str(record_sudo[eval("'" + field.field_name + "'")]) + "=value</h1>"
                    
                        if field.is_required:
                            primary_template += "<div class='form-group mb-2 s_website_form_required' data-type='char' data-name='" + field.field_name + "'>"
                        else:
                            primary_template += "<div class='form-group mb-2 ' data-type='char' data-name='" + field.field_name + "'>"                        
                        primary_template += "<label class='s_website_form_label' style='width: 200px' for='" + field.field_name + "'>"
                        primary_template += "<span class='s_website_form_label_content'>" + field.field_label + required_label + "</span>"
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

                                    #field_domain = safe_eval.safe_eval(field.field_domain)
                                m2o_id = request.env[field.field_model].sudo().search(field_domain)
                                domain_filter = str(field_domain).replace("'", "&#39;") if field_domain else ""
                                #primary_template += '<h2>' + str(domain_filter) + '/' + str(m2o_id.mapped('id')) + '</h2>'

                                #raise UserError(field_domain)
                                #field_domain = safe_eval(field.field_domain, {'user': request.env.user.partner_id.id})
                                
                                
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
                                
                                    #primary_template += "<input type='hidden'  id='join_fields' name='" + result + "' />"
                                    name = field.field_name +"-" + str(service.id) +"-" + field._name

                                    if field.is_required:
                                        primary_template += "<select id='" + field.field_name + "' name='" + field.field_name + "' required='" + required + "' data-model='" + field.field_id.relation + "' data-field='" + 'name' + "' data-search-fields='" + ','.join(search_fields) + "' data-label-fields='" + ','.join(label_fields) + "' data-domain='" + domain_filter + "'class='mb-2 select2-dynamic selection-search form-control'" +  " onchange='filter_field_vals(this, " + field.ref_populate_field_id.name + ")'>"
                                    else:
                                        primary_template += "<select id='" + field.field_name + "' name='" + field.field_name + "' data-model='" + field.field_id.relation + "' data-field='" + 'name' + "' data-search-fields='" + ','.join(search_fields) + "' data-label-fields='" + ','.join(label_fields) + "' data-domain='" + domain_filter + "'class='mb-2 select2-dynamic selection-search form-control'" +  " onchange='filter_field_vals(this, " + field.ref_populate_field_id.name + ")'>"
                                else:
                                    if field.is_required:
                                        primary_template += "<select id='" + field.field_name + "' name='" + field.field_name + "' required='" + required + "' data-model='" + field.field_id.relation + "' data-field='" + 'name' + "' data-search-fields='" + ','.join(search_fields) + "' data-label-fields='" + ','.join(label_fields) + "' data-domain='" + domain_filter + "'class='mb-2 select2-dynamic selection-search form-control'>"
                                    else:
                                        primary_template += "<select id='" + field.field_name + "' name='" + field.field_name + "' data-model='" + field.field_id.relation + "' data-field='" + 'name' + "' data-search-fields='" + ','.join(search_fields) + "' data-label-fields='" + ','.join(label_fields) + "' data-domain='" + domain_filter + "'class='mb-2 select2-dynamic selection-search form-control'>"
                                
                                
                                primary_template += "<option value='' >Select </option>"
                                for m in m2o_id:
                                    primary_template += "<option value='" + str(m.id) + "' " + (" selected" if record_val == m.id else " ") + ">"
                                    #template += "<t t-esc='t" + m.name + "'/>"
                                    primary_template += str(m.name)
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
                            domain_filter = str(field_domain).replace("'", "&#39;") if field_domain else ""

                            if field.is_required:
                                primary_template += "<select id='" + field.field_name + "' name='" + field.field_name + "' required='" + required + "' data-model='" + field.field_id.relation + "' data-field='" + 'name' + "' data-search-fields='" + ','.join(search_fields) + "' data-label-fields='" + ','.join(label_fields) + "' data-domain='" + domain_filter + "'class='form-control mb-2 select2-dynamic selection-search' multiple='multiple'>"
                            else:
                                primary_template += "<select id='" + field.field_name + "' name='" + field.field_name + "' data-model='" + field.field_id.relation + "' data-field='" + 'name' + "' data-search-fields='" + ','.join(search_fields) + "' data-label-fields='" + ','.join(label_fields) + "' data-domain='" + domain_filter + "'class='form-control mb-2 select2-dynamic selection-search' multiple='multiple'>"
                            for m in m2m_id:
                                primary_template += "<option value='' >Select </option>"
                                primary_template += "<option value='" + str(m.id) + "' " + (" selected" if record_val == m.id else " ") + ">"
                                primary_template += m.name
                                primary_template += "</option>"
                            primary_template += "</select>"

                        # Selection field
                        elif field.field_type == 'selection':
                            sel_ids = request.env['ir.model.fields.selection'].sudo().search([('field_id','=',field.field_id.id)])
                            primary_template += "<select id='" + str(field.field_name) + "' name='" + str(field.field_name) + "' required='" + required + "' data-model='" + str(field.field_id.relation) + "' data-field='" + 'name' + "' data-search-fields='" + ','.join(search_fields) + "' data-label-fields='" + ','.join(label_fields) + "' data-domain='" + domain_filter + "'class='form-control mb-2 select2-dynamic ' >"
                            for sel in sel_ids:
                                primary_template += "<option value='" + str(sel.value) + "' " + (" selected" if str(record_val) == sel.value else " ") + ">"
                                primary_template += sel.name
                                primary_template += "</option>"
                            primary_template += "</select>"
                    
                        # Date Field
                        elif field.field_type == 'date':
                            primary_template += '<input type="date" class="form-control mb-2 s_website_form_input"' + 'name="' + field.field_name + '"' + ' id="' + field.field_name + '"' + 'value="' + record_val + '"' +  ('required="1"' if field.is_required else '') + ">"
                        elif field.field_type == 'datetime':
                            if record_val:
                                data_pre = record_val.strip().split(',')
                                stDate = data_pre[0].replace("\"", "")
                                dat_time = datetime.datetime.strptime(stDate,'%Y-%m-%d %H:%M:%S.%f')
                            try:
                                primary_template += '<input type="datetime-local" class="form-control mb-2 s_website_form_input"' + 'name="' + field.field_name + '"' + ' id="' + field.field_name + '"' + 'value="' + dat_time + '"' +  ('required="1"' if field.is_required else '') + ">"
                            except:
                                stDate = stDate + ".4"
                                dat_time = datetime.datetime.strptime(stDate,'%Y-%m-%d %H:%M:%S.%f')
                                primary_template += '<input type="datetime-local" class="form-control mb-2 s_website_form_input"' + 'name="' + field.field_name + '"' + ' id="' + field.field_name + '"' + 'value="' + dat_time + '"' +  ('required="1"' if field.is_required else '') + ">"

                        elif field.field_type == 'char1':
                            primary_template += '<input type="text" class="form-control mb-2 s_website_form_input"' + 'name="' + field.field_name + '"' + ' id="' + field.field_name + '"' + 'value="' + record_val + '"' +  ('required="1"' if field.is_required else '') + ">"
                        elif field.field_type == 'text1':
                            primary_template += '<textarea class="form-control mb-2 s_website_form_input"' + 'name="' + field.field_name + '"' + ' id="' + field.field_name + '"' + 'value="' + record_val + '"' +  ('required="1"' if field.is_required else '') + " ></textarea>"
                        elif field.field_type in ('integer','float','monetary'):
                            primary_template += '<input type="number" step="any" class="form-control mb-2 s_website_form_input"' + 'name="' + field.field_name + '"' + ' id="' + field.field_name + '"' + 'value="' + record_val + '"' +  ('required="1"' if field.is_required else '') + ">"
                        else:
                            primary_template += (
                                '<input type="text" class="form-control mb-2 s_website_form_input" '
                                'name="' + field.field_name + '" '
                                'id="' + field.field_name + '" '
                                'onchange="filter_field_vals(this)" '
                                'value="111' + record_val + '" ' +
                                ('required="1" ' if field.is_required else '') +
                                '>'
                            )
                        primary_template += "</div>"
                primary_template += "</div>"                
                primary_template += "</div>"
                
                
                    
                primary_template += "</div>"
            primary_template += '</div>'
            # add seperator and button
            primary_template += '<nav class="navbar navbar-light navbar-expand-lg border p-2 py-0 mb-2 o_portal_navbar  mt-3 rounded">'
            primary_template += '<div class="d-flex flex-row col-6 text-right"/>'
            primary_template += '<button type="button" class="btn btn-link p-0 m-0 text-decoration-none" onclick="window.history.back();"  style="text-align: left;">Back</button>'
            primary_template += '</div>'
            primary_template += '<div class="d-flex flex-row-reverse col-6"/>'
            primary_template += '<button type="submit" class="btn btn-primary">Submit</button>'
            primary_template += '</div>'
            primary_template += '</nav>'
            primary_template += '<span id="s_website_form_result"/>'
            
            
        currency_ids = request.env['res.currency'].sudo().search([('active','=',True)])
        # JavaScript code as a string
        js_code = """
<script>
    function updateForm(formId) {
        console.log("Function updateForm started");
    
        let form = document.getElementById(formId);
        if (!form) {
            console.error("Form not found");
            return;
        }
    
        let modelId = document.getElementById("model_id").value;
        let formData = new FormData();
    
        // Collect all form elements' data
        for (let element of form.elements) {
            if (element.name && element.value) {
                formData.append(element.name, element.value);
            }
        }
        formData.append('model_id', modelId);
        alert(formData);
    
        // Send AJAX request with form data
        $.ajax({
            url: '/custom/get_form_vals',  // Your controller method URL
            type: 'POST',  // Use POST to send form data
            data: formData,
            processData: false,  // Prevent jQuery from automatically transforming the data into a query string
            contentType: false,  // Prevent jQuery from setting the Content-Type header
            dataType: 'json',  // Expect JSON response
            success: function (response) {
                console.log(response);
    
                // Loop through the response data and update corresponding form fields
                for (let fieldName in response) {
                    if (response.hasOwnProperty(fieldName)) {
                        let field = form.querySelector(`[name="${fieldName}"]`);
                        if (field) {
                            if (field.tagName === "SELECT") {
                                // Clear existing options
                                $(field).empty();
                                // Populate new options
                                for (let key in response[fieldName]) {
                                    if (response[fieldName].hasOwnProperty(key)) {
                                        $(field).append($('<option>', {
                                            value: key,
                                            text: response[fieldName][key]
                                        }));
                                    }
                                }
                            } else {
                                // Update field value for input, textarea, etc.
                                field.value = response[fieldName];
                            }
                        }
                    }
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.error("AJAX request failed: " + textStatus + ", " + errorThrown);
            }
        });
    }


    // End Function
    function filter_field_vals(element_src, element_target) {
        console.log("Function filter_field_vals started");

        let fieldNameSrc = element_src.name;  // Get the target element's name
        let fieldValueSrc = element_src.value;  // Get the element's value
        let FieldNameTarget = element_target.name // get the target element's name
        var modelId = document.getElementById("model_id").value;

        let data = {
            'src_field_name': fieldNameSrc,   // Send the field name
            'src_field_value': fieldValueSrc, // Send the field value
            'target_field_name': FieldNameTarget,  // Send the target field name
            'model_id': modelId // Send Model id
        };

            alert("Form data to be sent: " + JSON.stringify(formDataObject));

        $.ajax({
            url: '/custom/get_field_vals',
            type: 'GET',
            data: data,
            dataType: 'json',  // Explicitly expect JSON
            success: function (data) {
                console.log(data);
                //let targetSelect = $('#' + element_target);
                let targetSelect;
                if (typeof element_target === "string") {
                    targetSelect = $('#' + element_target);
                } else if (element_target instanceof HTMLElement) {
                    targetSelect = $(element_target);
                } else {
                    console.error("Invalid target provided");
                    return;
                }
    
                targetSelect.empty();
                for (let key in data) {
                    if (data.hasOwnProperty(key)) {
                        targetSelect.append($('<option>', {
                            value: key,
                            text: data[key]
                        }));
                    }
                }
            },
        });
    }

// Dynamic Search JS Code
/*
$(document).ready(function() {
    $('.select2-dynamic').each(function() {
        var model = $(this).data('model');
        var field = $(this).data('field');
        
        $(this).select2({
            ajax: {
                url: '/dynamic_search',
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        q: params.term, // search term
                        model: model,
                        field: field,
                        page: params.page
                    };
                },
                processResults: function (data) {
                    return {
                        results: data.items
                    };
                },
                cache: true
            },
            placeholder: 'Search...',
            minimumInputLength: 1
        });
    });
});
*/
$(document).ready(function() {
    console.log("Initializing Select2...");
    $('.select2-dynamic').each(function() {
        var model = $(this).data('model');
        var field = $(this).data('field');
        var searchFields = $(this).data('search-fields');
        var domain = $(this).data('domain');
        var labelFields = $(this).data('label-fields');
        
        $(this).select2({
            ajax: {
                url: '/dynamic_search',
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        q: params.term,
                        model: model,
                        field: field,
                        search_fields: searchFields,
                        domain: domain,
                        label_fields: labelFields,
                        page: params.page
                    };
                },
                processResults: function (data) {
                    return {
                        results: data.items
                    };
                },
                cache: true
            },
            placeholder: 'Search...',
            minimumInputLength: 1
        });
    });
});



</script>

        """
        #js_code = ''

        return {
            'currency_ids': currency_ids,
            'template_primary_fields': primary_template,
            'template_extra_fields': extra_template,
            'service_id': service_id,
            'record_id': record_id,
            'model_id': model_id,
            'edit_mode': edit_mode or 0,
            'js_code': js_code,
        }
    
    @http.route(['/my/model/record/<int:service_id>/<int:model_id>/<int:record_id>/<int:edit_mode>'
                ], type='http', auth="user", website=True)        
    def portal_hr_service_record(self, service_id=False, model_id=False, record_id=False, edit_mode=False, js_code=False,**kw):
        
        service_sudo = request.env['hr.service'].sudo().search([('id','=',service_id)],limit=1)
        # Assuming you have the group ID
        group_id = service_sudo.group_id.id  # Replace with your group ID
        # Check if the user belongs to the group using the group ID
        user = request.env.user
        user_groups = user.groups_id.ids  # This will give you a list of group IDs the user belongs to
        if group_id not in user_groups:
            # If the user doesn't belong to the group, redirect them to another page (e.g., the home page)
            return request.redirect('/my')

        return request.render("de_portal_hr_service.portal_service_record_form", self._prepare_service_record_page(service_id, model_id, record_id, edit_mode, js_code))
        
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


            #if service_id.filter_field_id:
            #    domain = [(service_id.filter_field_id.name, 'child_of', [request.env.user.partner_id.id]),
            #    (service_id.filter_field_id.name, '=', [request.env.user.partner_id.id])]
   
            #if service_id.filter_domain:
            #    domain = safe_eval.safe_eval(service_id.filter_domain) + domain

            
            #model_records = request.env[service_id.header_model_id.model].sudo().search(domain).ids
            model_records = service_id._get_records_filter_by_domain(request.env.user.partner_id.id)
            
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
            
                
    @http.route(['/my/model/record/prev/<int:service_id>/<int:model_id>/<int:record_id>'
                ], type='http', auth="user", website=True)        
    def portal_hr_service_record_previous(self, service_id=False, model_id=False, record_id=False, edit_mode=False, **kw):
        
        return request.render("de_portal_hr_service.portal_service_record_form", self._prepare_service_record_page(service_id, model_id, record_id, edit_mode, js_code))
        
    
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

        user_id = request.env['res.users'].sudo().search([('id','=',http.request.env.context.get('uid'))],limit=1)
        vals = {}
        employee_id = request.env['hr.employee']
        
        if service_id.header_model_id.id == int(model_id):
            service_items = service_id.hr_service_items.filtered(lambda x: x.operation_mode)
            if edit_mode == '1' or edit_mode == 1:
                record_sudo = request.env[service_id.header_model_id.model].sudo().search([('id','=',int(record_id))],limit=1)
                res_name = record_sudo.name

            # default values for header model
            for field in service_id.header_model_id.field_id.filtered(lambda r: r.relation and r.ttype == 'many2one' and r.store):
                if not kw.get(field.name):
                    if field.relation == 'res.users':
                        vals.update({
                            field.name: user_id.id,
                        })
                    if field.relation == 'hr.employee':
                        employee_id = request.env['hr.employee'].sudo().search([('user_id','=',http.request.env.context.get('uid'))],limit=1)
                        if employee_id:
                            vals.update({
                                field.name: user_id.employee_id.id,
                            })
                        else:
                            raise UserError('Employees are allowed only to process this transactions')
                    if field.relation == 'res.partner':
                        vals.update({
                            field.name: user_id.partner_id.id,
                        })
        elif line_item.line_model_id: #service_id.line_model_id.id == int(model_id):
            service_items = line_item.hr_service_record_line_items #line_model_id.hr_service_record_line_items #.hr_service_items_line
            if edit_mode == '1' or edit_mode == 1:
                record_sudo = request.env[line_item.line_model_id.model].sudo().search([('id','=',int(record_id))],limit=1)
                res_name = record_sudo.name
                # default values for header model
            for field in line_item.line_model_id.field_id.filtered(lambda r: r.relation and r.ttype == 'many2one' and r.store):
                if not kw.get(field.name):
                    if field.relation == 'res.users':
                        vals.update({
                            field.name: user_id.id,
                        })
                    if field.relation == 'hr.employee':
                        vals.update({
                            field.name: user_id.employee_id.id,
                        })
                    if field.relation == 'res.partner':
                        vals.update({
                            field.name: user_id.partner_id.id,
                        })
        
        
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
                elif field.field_type in ('float','monetary'):
                    vals.update({
                        field.field_name: float(kw.get(field.field_name))
                    })
                elif field.field_type in ('integer'):
                    vals.update({
                        field.field_name: int(kw.get(field.field_name))
                    })
                elif field.field_type == 'datetime':
                    raise UserError(field.field_type)
                    vals.update({
                        field.field_name: datetime.datetime.strptime(kw.get(field.field_name),'%Y-%m-%dT%H:%M')
                        #(kw.get(field.field_name))
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
                #record_sudo.message_subscribe(partner_ids=[request.env.user.partner_id.id])
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
        
        # Assuming you have the group ID
        group_id = service_id.group_id.id  # Replace with your group ID
        # Check if the user belongs to the group using the group ID
        user = request.env.user
        user_groups = user.groups_id.ids  # This will give you a list of group IDs the user belongs to
        if group_id not in user_groups:
            # If the user doesn't belong to the group, redirect them to another page (e.g., the home page)
            return request.redirect('/my')
            
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

        # Assuming you have the group ID
        group_id = service_id.group_id.id  # Replace with your group ID
        # Check if the user belongs to the group using the group ID
        user = request.env.user
        user_groups = user.groups_id.ids  # This will give you a list of group IDs the user belongs to
        if group_id not in user_groups:
            # If the user doesn't belong to the group, redirect them to another page (e.g., the home page)
            return request.redirect('/my')
            
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
            
