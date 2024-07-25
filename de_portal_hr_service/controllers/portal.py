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

js_script = ""

class CustomerPortal(portal.CustomerPortal):
    
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

    @http.route('/get/default_values', type='http', auth='public', methods=['GET'], csrf=False)
    def _get_default_values(self, **kwargs):
        service_id = kwargs.get('service_id')
        model_id = kwargs.get('model_id')
        record_id = kwargs.get('record_id') or 0
        
        field_id = kwargs.get('field_id')
        field_model = kwargs.get('field_model')
        field_name = kwargs.get('field_name')

        service = request.env['hr.service'].browse(int(service_id))        
        changeable_field_ids = json.loads(kwargs.get('changeable_field_ids', '[]'))
        fields = request.env['ir.model.fields'].browse(changeable_field_ids)

        form_data = request.params
        form_elements = [{'name': name, 'value': form_data[name]} for name in form_data]
        form_elements_json = json.dumps(form_elements)

        options = {
            'field_data': service._get_default_field_values(form_elements_json, changeable_field_ids, field_name),
        }

        return json.dumps(options)
        

    @http.route('/get/list_values', type='http', auth='public', methods=['GET'], csrf=False)
    def _get_list_values(self, **kwargs):
        service_id = kwargs.get('service_id')
        model_id = kwargs.get('model_id')
        record_id = kwargs.get('record_id') or 0
        
        field_id = kwargs.get('field_id')
        field_model = kwargs.get('field_model')
        field_name = kwargs.get('field_name')

        service = request.env['hr.service'].browse(int(service_id))        

        form_data = request.params
        form_elements = [{'name': name, 'value': form_data[name]} for name in form_data]
        form_elements_json = json.dumps(form_elements)

        options = {
            'field_data': service._get_list_values(form_elements_json, field_name),
            #'form_data': form_elements_json,
            #'field_name': field_name,
        }
        #options = {
        #    'unit':1,
        #    'kg':2,
        #}
        return json.dumps(options)

    

    
    
    @http.route('/get/recomputed_values', type='http', auth='public', methods=['GET'], csrf=False)
    def recompute_field_values(self, **kwargs):
        """
        1. Find the realted records from changeable fields
        2. get the expression values from the related records
        3. devide the expression into artithmatic operators e.g product_id.list_price + product_uom.id
        4. get the current web selected values of before dot expression e.g product_id and product_uom
        5. find the related model of these before dot expression items e.g product_id and product_uom
        6. get the current record on the basis of point no. 4 and point no. 5
        7. get the expression values with current record and perform arithmatic operations
        8. return the values and field names
        9. update the field values through javascript
        """
        service_id = kwargs.get('service_id')
        model_id = kwargs.get('model_id')
        record_id = kwargs.get('record_id') or 0
        field_id = kwargs.get('field_id')
        field_model = kwargs.get('field_model')
        field_name = kwargs.get('field_name')
        field_value = kwargs.get('field_value')
        populate_field_id = kwargs.get('populate_field_id')

        service = request.env['hr.service'].browse(int(service_id))        
        # Retrieve and parse the many2many field IDs
        changeable_field_ids = json.loads(kwargs.get('changeable_field_ids', '[]'))
        # Fetch the field names from ir.model.fields
        fields = request.env['ir.model.fields'].browse(changeable_field_ids)        
        # Fetch the values for these fields from the specified model and record
        #model = request.env[field_model]
        #record = model.browse(int(field_value))
        # Prepare field data in a loop
        field_data = {}
        #for field in fields:
        #    field_name = field.name
        #    field_data[field_name] = service.get_field_value_from_expression(int(model_id),field_model,field_name, int(field_value),changeable_field_name)#record.id


        form_data = request.params

        # Prepare list of dictionaries containing element names and values
        form_elements = [{'name': name, 'value': form_data[name]} for name in form_data]

        # Convert the list of dictionaries to JSON format
        form_elements_json = json.dumps(form_elements)
        
        
        options = {
            #'service_id': service_id,
            #'model_id': model_id,
            #'record_id': record_id,
            #'field_id': field_id,
            #'field_model': field_model,
            #'field_name': field_name,
            #'field_value': field_value,
            #'populate_field_id': populate_field_id,
            #'changeable_field_ids': changeable_field_ids,
            'field_data': service.get_changeable_field_values(form_elements_json, changeable_field_ids, field_name),
            #'form_elements_json': form_elements_json,
        }

        return json.dumps(options)
        
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
    
        template, js_code = self._generate_dynamic_form(service, hr_service_items, record_sudo)
    
        currency_ids = request.env['res.currency'].sudo().search([('active', '=', True)])
        #js_code = self._generate_js_code() + js_code
    
        return {
            'currency_ids': currency_ids,
            'template_primary_fields': template,
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
        template = self._get_base_template(service)
        js_template = ''
    
        hr_service_grouped_items = self._group_service_items(service)
        for key, group in sorted(hr_service_grouped_items.items()):
            template += self._get_column_template(group)
    
            for field in hr_service_items.filtered(lambda x: x.field_variant_line_id.id == key.id):
                record, required, required_label, readonly = self._get_field_properties(field, record_sudo)
    
                html_data, js_script = self._generate_field_template(field, service, record, required, required_label,readonly)
                template += html_data
                js_template += js_script
    
            template += "</div></div></div>"
    
        template += self._get_footer_template()

        js_script = """
        <script type="text/javascript">
            $(document).ready(function() {{
                $('.select2-dynamic').select2({{
                    theme: 'bootstrap4',
                    placeholder: 'Select an option',
                    allowClear: true
                }});
        
                {js_template}
            }});
        </script>
        """.format(js_template=js_template)



    
        return template, js_script
    
    def _get_base_template(self, service):
        return '''
        <link href="/de_portal_hr_service/static/src/select_two.css" rel="stylesheet" />
        <script type="text/javascript" src="/de_portal_hr_service/static/src/js/jquery.js"></script>
        <script type="text/javascript" src="/de_portal_hr_service/static/src/js/select_two.js"></script>
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
        record = ''
        if record_sudo:
            record = str(record_sudo[field.field_name]) if field.field_type != 'many2one' else record_sudo[field.field_name]
        required = '1' if field.is_required else ''
        required_label = '*' if field.is_required else ''
        readonly = "readonly=1" if field.field_readonly else ''
        return record_sudo, required, required_label, readonly
    
    def _generate_field_template(self, field, service, record, required, required_label,readonly):
        js_script = ''
        js = ''
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
            select_tag, js = self._generate_many2one_field(field, service, record, required,readonly)
            template += select_tag
            js_script += js
        elif field.field_type == 'many2many':
            template += self._generate_many2many_field(field, record, required)
        elif field.field_type == 'selection':
            template += self._generate_selection_field(field, record, required,readonly)
        elif field.field_type == 'date':
            template += '<input type="date" class="form-control mb-2 s_website_form_input" name="{field_name}" id="{field_name}" value="{record_id}" {required}>'.format(
                field_name=field.field_name, 
                record_id=record.id, required='required="1"' if required else '',
                readonly=readonly
            )
        elif field.field_type == 'datetime':
            template += self._generate_datetime_field(field, record, required,readonly)
        elif field.field_type in ('integer', 'float', 'monetary'):
            template += '<input type="{input_type}" class="form-control mb-2 s_website_form_input" name="{field_name}" id="{field_name}" value="{record_id}" {required} {readonly}>'.format(
                input_type='number' if field.field_type in ('integer', 'float', 'monetary') else 'text',
                field_name=field.field_name, 
                record_id=record.id, 
                required='required="1"' if required else '',
                readonly=readonly
            )
        else:
            template += '''
            <input type="text" class="form-control mb-2 s_website_form_input" name="{field_name}" id="{field_name}" onchange="filter_field_vals(this)" value="{record_id}" {required} {readonly}>
            '''.format(field_name=field.field_name, 
                       record_id=record.id, 
                       required='required="1"' if required else '',
                       readonly=readonly
                      )
    
        template += "</div>"
        return template, js_script
    
    def _generate_many2one_field(self, field, service, record, required,readonly):
        field_domain = self._get_field_domain(field)
        m2o_id = request.env[field.field_model].sudo().search(field_domain)
        domain_filter = str(field_domain).replace("'", "&#39;") if field_domain else ""
    
        if field.field_model == 'ir.attachment':
            return '''
            <input type='file' class='form-control-file mb-2 s_website_form_input' id='{field_name}' name='{field_name}' multiple='1' />
            '''.format(field_name=field.field_name
                      )


        data = {
            'model_id': service.header_model_id.id,
            'service_id': service.id,
        }
        form_id = 'form'+ str(service.id)

        js_script = """
            $(document).ready(function() {{
                $('#{form_id}').on('change', '#{field_name}', function() {{
                    let form_data = $('#{form_id}').serialize();  // Serialize the form data
                    
            
                    $.ajax({{
                        url: '/get/list_values',
                        type: 'GET',
                        data: form_data + '&field_id={field_id}&field_name={field_name}&field_model={field_model}&changeable_field_ids={changeable_field_ids}',
                        dataType: 'json',
                        success: function(data) {{
                            console.log(data);

                            // Loop through each field in the field_data
                            for (let field_name in data.field_data) {{
                                let field_values = data.field_data[field_name];
                                let fieldElement = $('#' + field_name);

                                if (fieldElement.length) {{
                                    fieldElement.empty();  // Clear existing options

                                    // Add new options to the select field
                                    for (let option_text in field_values) {{
                                        let option_value = field_values[option_text];
                                        fieldElement.append(new Option(option_text, option_value));
                                    }}
                                }}
                            }}
                            
                        }},
                        error: function(error) {{
                            console.error('Error fetching data:', error);
                        }}
                    }});
                    // Second AJAX Call Start
                    $.ajax({{
                        url: '/get/default_values',
                        type: 'GET',
                        data: form_data + '&field_id={field_id}&field_name={field_name}&field_model={field_model}&changeable_field_ids={changeable_field_ids}',
                        dataType: 'json',
                        success: function(data) {{
                            console.log(data);
                            // Update the fields dynamically based on the response
                            let fieldData = data.field_data.computed_field_values;
                            for (let field in fieldData) {{
                                if (document.getElementById(field)) {{
                                    document.getElementById(field).value = fieldData[field];
                                }}
                            }}
                        }},
                        error: function(error) {{
                            console.error('Error fetching data:', error);
                        }}
                    }});
                    // Second AJAX Call End
                }});
            }});
            """.format(
                    form_id=form_id, 
                    field_name=field.field_name, 
                    field_id=field.id, 
                    field_model=field.field_model, 
                    changeable_field_ids=json.dumps(field.ref_changeable_field_ids.ids)
                )

            
        search_fields = ','.join(field.search_fields_ids.mapped('name'))
    
        select_tag = '''
        <select id='{field_name}' name='{field_name}' {required} {readonly} data-model='{field_model}' data-field='name' data-search-fields='{search_fields}' data-domain='{domain_filter}' class='mb-2 select2-dynamic selection-search form-control'>
            <option value=''>Select</option>
        '''.format(
                field_name=field.field_name, 
                required='required="1"' if required else '',
                readonly=readonly,
                field_model=field.field_model, 
                search_fields=search_fields, 
                domain_filter=domain_filter
        )
    
        for rec in m2o_id:
            selected = 'selected="selected"' if rec.id == record.id else ''
            #combined_label = ' '.join([str(rec[label]) for label in field.label_fields_ids.mapped('name') if rec[label]])
            select_tag += "<option value='{id}' {selected}>{name}</option>".format(id=rec.id, selected=selected, name=rec[field.link_field_id.name])
    
        select_tag += "</select>"
        return select_tag, js_script




    
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
    
    def _generate_selection_field(self, field, record_val, required, readonly):
        selection_template = '''
        <select id='{field_name}' name='{field_name}' {required} {readonly} class='selection-search form-control mb-2'>
        '''.format(
                field_name=field.field_name, 
                required='required="1"' if required else '',
                readonly=readonly
            )
    
        for val, label in eval(field.field_selection):
            selected = 'selected="selected"' if val == record_val else ''
            selection_template += "<option value='{val}' {selected}>{label}</option>".format(val=val, selected=selected, label=label)
    
        selection_template += "</select>"
        return selection_template
    
    def _generate_datetime_field(self, field, record_val, required,readonly):
        return '''
        <input type="datetime-local" class="form-control mb-2 s_website_form_input" name="{field_name}" id="{field_name}" value="{record_val}" {required} {readonly}>
        '''.format(
                field_name=field.field_name, 
                record_val=record_val, 
                required='required="1"' if required else '',
                readonly=readonly
            )
    
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
            try:
                return eval(field.field_domain)
            except:
                return []
        return []

    
    
    

    # End Service Record Page

    
    
    
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

    # Message Record
    @http.route('/my/message/<int:service_id>/<int:model_id>/<int:record_id>', website=True, page=True, auth='public', csrf=False)
    def user_messsage(self, **kw):
        service_id = kw.get('service_id')
        model_id = kw.get('model_id')
        record_id = kw.get('record_id')

        user = request.env.user
        
        message = kw.get('message')
        #user_ids = kw.get('user_ids[]')
        user_ids = request.httprequest.form.getlist('user_ids')

        
        service = request.env['hr.service'].sudo().browse(int(service_id))
        model = request.env['ir.model'].sudo().browse(int(model_id))
        record = request.env[model.model].sudo().browse(int(record_id))

        # Handle file attachments
        files = request.httprequest.files.getlist('attachments')

        attachment_files  = request.httprequest.files.getlist('attachments')
        
        
        service.create_message(model, record, user, message, attachment_files, user_ids)
        return request.redirect('/my/model/record/%s/%s/%s' % (service.id,model.id, record.id))


    @http.route('/my/record/schedule-activity', type='http', auth='public', website=True, csrf=False)
    def schedule_activity(self, **kwargs):
        service_id = int(kwargs.get('service_id'))
        record_id = int(kwargs.get('record_id'))
        model_id = int(kwargs.get('model_id'))
        activity_type_id = int(kwargs.get('activity_type'))
        due_date = kwargs.get('due_date')
        summary = kwargs.get('summary')
        user_id = kwargs.get('user_id')
        details = kwargs.get('details')
            
        if due_date:
            due_date = datetime.datetime.strptime(due_date, '%Y-%m-%d')
            
        model = request.env['ir.model'].browse(model_id).model

        # Create the activity
        activity_vals = {
                'res_model_id': model_id,
                'res_id': record_id,
                'activity_type_id': activity_type_id,
                'summary': summary,
                'user_id': user_id,
                'note': details,
                'date_deadline': due_date,
        }
        
        request.env['mail.activity'].sudo().create(activity_vals)
        return request.redirect('/my/model/record/%s/%s/%s' % (service_id,model_id, record_id))

    @http.route('/my/record/schedule-activity-done', type='http', auth='public', website=True, csrf=False)
    def mark_activity_done(self, **kwargs):
        service_id = int(kwargs.get('service_id'))
        record_id = int(kwargs.get('record_id'))
        model_id = int(kwargs.get('model_id'))
        activity_id = int(kwargs.get('activity_id'))
        remarks = kwargs.get('remarks')
        
        activity = request.env['mail.activity'].browse(int(activity_id))
        if activity.exists():
            activity.action_feedback(feedback=remarks)
        return request.redirect('/my/model/record/%s/%s/%s' % (service_id,model_id, record_id))

    @http.route('/my/record/schedule-activity-done-and-next', type='http', auth='public', website=True, csrf=False)
    def mark_activity_done_and_schedule_next(self, **kwargs):
        service_id = int(kwargs.get('service_id'))
        record_id = int(kwargs.get('record_id'))
        model_id = int(kwargs.get('model_id'))
        activity_id = int(kwargs.get('activity_id'))
        remarks = kwargs.get('remarks')
    
        #raise UserError(f"Service ID: {service_id}, Record ID: {record_id}, Model ID: {model_id}, Activity ID: {activity_id}, Remarks: {remarks}")

    
        activity = request.env['mail.activity'].browse(int(activity_id))
        if activity.exists():
            activity.action_feedback(feedback=remarks)
        
        return request.make_response(json.dumps({'status': 'success'}), headers={'Content-Type': 'application/json'})
    


