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
        if 'service_count' in counters:
            values['service_count'] = request.env['hr.service'].search_count([]) \
                if request.env['hr.service'].check_access_rights('read', raise_exception=False) else 0
        return values
    
    
    # ------------------------------------------------------------
    # My Services
    # ------------------------------------------------------------
    def _service_get_page_view_values(self, service, access_token, **kwargs):
        values = {
            'page_name': 'service',
            'service': service,
        }
        return self._get_page_view_values(service, access_token, values, 'my_services_history', False, **kwargs)
    
    @http.route(['/my/services', '/my/services/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_hr_services(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Service = request.env['hr.service']
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        #if date_begin and date_end:
        #    domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # Service count
        service_count = Service.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/services",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=service_count,
            page=page,
            step=self._items_per_page
        )
        domain += [('state','=','publish')]
        # content according to pager and archive selected
        services = Service.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_services_history'] = services.ids[:100]
        
        values.update({
            'date': date_begin,
            'date_end': date_end,
            'services': services,
            'page_name': 'service',
            'default_url': '/my/services',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("de_portal_hr_service.portal_my_hr_services", values)
    
    
    
    def _service_records_get_page_view_values(self, service, access_token, **kwargs):
        values = {
            'page_name': 'records',
            'service': service,
        }
        return self._get_page_view_values(service, access_token, values, 'my_services_history', False, **kwargs)
    
    @http.route(['/my/<int:service_id>',
                 '/my/<int:service_id>/page/<int:page>'
                ], type='http', auth="public", website=True)
    # @http.route(['/my/service/<int:service_id>',
    #              '/my/service/<int:service_id>/page/<int:page>'
    #             ], type='http', auth="public", website=True)
    def portal_my_hr_service(self, service_id=None, access_token=None, **kw):
        try:
            service_sudo = self._document_check_access('hr.service', service_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        #raise UserError(str(service_sudo.name))
        values = self._service_records_get_page_view_values(service_sudo, access_token, **kw)
        values.update({
            'portal_hr_service_dyanmic_page_template': self.portal_hr_service_dyanmic_page_template(service_sudo),
        })
        return request.render("de_portal_hr_service.portal_my_hr_service", values)
    
    
    
    # -------------------------------------------
    # My Records
    # -------------------------------------------
    def _model_record_get_page_view_values(self, service_id, model_id, record_id, access_token, **kwargs):
        values = {
            'page_name': 'modelrecords',
            #'service': service_id,
            #'record_id': record_id,
            #'model_id': model_id,
            #'access_token': access_token,
            #'record_id': record_id,
        }
        
        return self._get_page_view_values(service_id, access_token, values, 'my_services_history', False, **kwargs)
    
    @http.route('/my/model/record/<int:service_id>/<int:model_id>/<int:record_id>', type='http', auth='public', website=True)
    def portal_my_hr_service_record(self, page=1, service_id=None, model_id=None, record_id=None, access_token=None, **kw):
        try:
            service_sudo = self._document_check_access('hr.service', service_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        Record = request.env[service_sudo.header_model_id.model]
        if access_token:
            Record = Record.sudo()
        
        line_item = request.env['hr.service.record.line'].search([('hr_service_id','=',service_id),('line_model_id','=',int(model_id))],limit=1)

        # find the model record
        if service_sudo.header_model_id.id == model_id:
            record_sudo = Record.search([('id', '=', record_id)], limit=1).sudo()
        elif line_item.line_model_id.id == model_id:
            record_sudo = Record.search([('id', '=', record_id)], limit=1).sudo()
        #task_sudo.attachment_ids.generate_access_token()

        print(record_sudo)

        # record_sudo['expense_line_ids']
        values = self._model_record_get_page_view_values(service_sudo, model_id, record_sudo, access_token, **kw)
        #values = self._record_get_page_view_values(service_id, access_token, **kw)
        #values['service'] = service_sudo
        values.update({
            'service': service_sudo,
        })
        #raise UserError(_(values))
        #values = {
        #    'service': service_sudo,
        #}
        
        record_title = record_state = ''
        
        if service_sudo.title_field_id.name:
            if service_sudo.title_field_id.ttype == 'many2one':
                record_title = record_sudo[eval("'" + service_sudo.sudo().title_field_id.name + "'")].name
            else:
                record_title = str(record_sudo[eval("'" + service_sudo.sudo().title_field_id.name + "'")])
                
        if service_sudo.state_field_id.name:
            if service_sudo.state_field_id.ttype == 'many2one':
                record_state = record_sudo[eval("'" + service_sudo.sudo().state_field_id.name + "'")].name
            elif service_sudo.state_field_id.ttype == 'selection':
                sel_id = request.env['ir.model.fields.selection'].sudo().search([('field_id','=',service_sudo.state_field_id.id),('value','=',record_sudo[eval("'" + service_sudo.sudo().state_field_id.name + "'")])],limit=1)
                if sel_id:
                    record_state = str(sel_id.name)

            else:
                record_state = str(record_sudo[eval("'" + service_sudo.sudo().state_field_id.name + "'")])
        
        # find editable record option
        record_editable = False
        if service_sudo.condition:
            domain = safe_eval.safe_eval(service_sudo.condition)
            record_editable = False
            if record_sudo.filtered_domain(domain):
                record_editable = True
            else:
                record_editable = False
        else:
            record_editable = True
        try:
            partner_id = request.env.user.partner_id
            record_sudo.message_subscribe([partner_id.id])
        except Exception as e:
            print(e)

    #   values['record_id']['expense_line_ids'][1]          
        values.update({
            'portal_hr_service_record_dyanmic_page_template': self.portal_hr_service_record_dyanmic_page_template(service_sudo,record_sudo),
            'record_id': record_sudo,
            'title': record_title.upper(),
            'state': record_state.upper(),
            'record_editable': record_editable,
            'allow_messages': service_sudo.allow_messages,
        })
        return request.render("de_portal_hr_service.portal_my_hr_service_record", values)

    
    # -------------------------------------------
    # Custom html generation
    # -------------------------------------------
    def _get_portal_my_entries_content(self,entries):
        template = ''
        # Dynamic Header
        for entry in entries:
            template += '<strong>' + str(entry.name) + '</strong><br/>'
    # -------------------------------------------
    # Custom html generation for list page
    # -------------------------------------------
    def portal_hr_service_dyanmic_page_template(self,service_id):
        # TEMPORARY RETURNS CONSTANT FOR DEVELOPMENT PURPOSE
        m2m_ids = False
        fields = ''
        template = ''
        counter = 0
        m2m_text = ''
        rec_id = model_id = ''
        #service = request.env['hr.service'].sudo([('id','=',int(service_id))])
        #s_id = request.env['hr.service'].search([('id','=',service.id)],limit=1)
        domain = []
        message_partner_ids = request.env['ir.model.fields'].sudo().search([('name','=','message_partner_ids'),('model','=',service_id.header_model_id.model)],limit=1)
        employee_id = request.env['ir.model.fields'].sudo().search([('name','=','employee_id'),('model','=',service_id.header_model_id.model)],limit=1)
        partner_id = request.env['ir.model.fields'].sudo().search([('name','=','partner_id'),('model','=',service_id.header_model_id.model)],limit=1)
        # field_filter_id = request.env['ir.model.fields'].sudo().search([('name','=','filter_field_id'),('model','=','hr.service')],limit=1)
        if service_id.filter_field_id:
            domain = [(service_id.filter_field_id.name, 'child_of', [request.env.user.partner_id.id]),
            (service_id.filter_field_id.name, '=', [request.env.user.partner_id.id])]
        # elif employee_id:
        #     domain = [('employee_id', '=', [request.env.user.employee_id.id])]
        # elif partner_id:
        #     domain = [('partner_id', '=', [request.env.user.partner_id.id])]
        if service_id.filter_domain:
            domain = safe_eval.safe_eval(service_id.filter_domain) + domain
            
        records = request.env[service_id.header_model_id.model].search(domain)
        # records = request.env[service_id.header_model_id.model].search(domain,offset=offset, limit=limit)
        
        # template += '<link href="https://cdn.datatables.net/1.13.1/css/jquery.dataTables.min.css" rel="stylesheet" />'
        # template += '<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>'
        # template += '<script type="text/javascript" src="https://cdn.datatables.net/1.13.1/js/jquery.dataTables.min.js"></script>'
        # template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/main_datatable.js"></script>'
      
      
        template += '<link href="/de_portal_hr_service/static/src/datatable.css" rel="stylesheet" />'
        template += '<link href="/de_portal_hr_service/static/src/datatable_export_button.css" rel="stylesheet" />'
        template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/jquery.js"></script>'
        template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/datatable.js"></script>'
        
        template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_buttons.js"></script>'
        template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_jszip.js"></script>'
        template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_pdfmake.js"></script>'
        template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_vfs_fonts.js"></script>'
        template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_btn_html5.js"></script>'
        template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_print.js"></script>'
        template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_select.js"></script>'

        template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/main_datatable.js"></script>'

        if service_id.is_create:
            template += "<t class='col-lg-6 col-md-4 mb16 mt32'>"
            template +=  "<a href='/my/model/record/" + str(service_id.id) + "/" + str(service_id.header_model_id.id) + "/0/0" + "' class='btn btn-primary pull-left' >Create " + str(service_id.name) + "</a>"
            template += "<br></br></t>"

        model_id = service_id.header_model_id.id
        # template += "<div class = 'card-body'>"
        template += "<table class='myTable mt-2 cell-border '>"
        # template += "<table class='myTable mt-2 cell-border stripe'>"
        template += "<thead class='bg-100'>"
        if self._get_service_records_labels_before(service_id):
            template += self._get_service_records_labels_before(service_id)
        for label in service_id.hr_service_items:
            if label.display_option in ('list','both'):
                template += "<th>" + label.field_label + "</th>"
            
        if self._get_service_records_labels_after(service_id):
            template += self._get_service_records_labels_after(service_id)
        template += "</thead>"
        
        # fetch records
        template += "<tbody class='sale_tbody'>"
        for line in records:
            counter += 1
            
            # if counter % 2 == 0:
                # template += "<tr class='bg-primary text-white'>"
                # template += "<tr class='bg-200'>"
            # else:
            template += "<tr>"
            
            if self._get_service_records_row_cols_before(service_id,line):
                template += self._get_service_records_row_cols_before(service_id,line)
            for f in service_id.hr_service_items:
                # Start
                template += self._get_service_records_row(f,service_id,line)
                # template += self._get_service_records_row(f,service_id,line)
                #End
            if self._get_service_records_row_cols_after(service_id,line):
                template += self._get_service_records_row_cols_after(service_id,line)
            template += "</tr>"
        template += "</tbody>"
        template += "</table>"
       
        return template
        # template +=  "<a href='/items/" + str(page_number)  + "' class='page-link pull-left' >Previous " +  "</a>"
        # <a t-att-href="javascript:handlePagination(1)" t-if="current_page > 1">Previous</a>
        # <a t-att-href="javascript:handlePagination(current_page + 1)" t-if="(offset + limit) < items_count">Next</a>
        # template += "<a class='page-link'" + " t-if='#{page_number} > 1' " + "t-attf-href= '/items?page= #{previous_page_number} '>Previous</a>" 
        # template += "<a class='page-link'" + "t-attf-onclick='goToPage()'>Previous</a>" 
    
    def _get_service_records_labels_before(self,service_id):
        template = ''
        return template
    
    def _get_service_records_labels_after(self,service_id):
        template = ''
        return template
    
    def _get_service_records_row_cols_before(self,service_id,record):
        template = ''
        return template
    
    def _get_service_records_row_cols_after(self,service_id,record):
        template = ''
        return template
    
    def _get_service_records_row(self,f,service_id,line):
        template = ''
        rec_id = False
        rec_id = str(line["id"])
        #fields += f.field_name + ','
        if f.display_option in ('list','both'):
            template += "<td style='text-overflow: clip;'>"
            if f.link_record:
                #template +=  "<a href='/my/record?id='{" + str(f.id) + "'}'>"

                # if counter % 2 == 0:
                #     template +=    '<a class="bg-primary text-white" href="/my/model/record/' + str(service_id.id) + '/' + str(service_id.header_model_id.id) + '/' + str(rec_id) + '">'
                # else:
                template +=    '<a href="/my/model/record/' + str(service_id.id) + '/' + str(service_id.header_model_id.id) + '/' + str(rec_id) + '">'

            if f.field_id.id == service_id.state_field_id.id:
                template += '<span class="badge badge-pill badge-secondary">'

            """
            =================================================================================
                Display records 
            =================================================================================
            """
            #template += eval("'" + f.field_name + "'")
            if line[eval("'" + f.field_name + "'")]:
                if f.field_type == 'many2one':
                    template += str(line[eval("'" + f.sudo().field_name + "'")].name)
                    #if line[eval("'" + f.field_name + "'")].check_access_rights('read', raise_exception=False) else 0

                elif f.field_type == 'many2many':
                    m2m_ids = request.env[f.field_model].sudo().search([('id','in',line[eval("'" + f.field_name + "'")].ids)])
                    #if m2m_ids.check_access_rights('read', raise_exception=False) else 0
                    m2m_text = ''
                    for m2m in m2m_ids:
                        m2m_text += m2m.name + ','
                    template += m2m_text[:-1]
                    #template += str(line[eval("'" + f.field_name + "'")].ids)
                elif f.field_type == 'selection':
                    sel_id = request.env['ir.model.fields.selection'].sudo().search([('field_id','=',f.field_id.id),('value','=',line[eval("'" + f.field_name + "'")])],limit=1)
                    if sel_id:
                        template += str(sel_id.name.capitalize())
                else:
                    template += str(line[eval("'" + f.field_name + "'")])
                
            if f.link_record:
                template += "</a>"
            if f.field_id.id == service_id.state_field_id.id:
                template += '</span>'
                    
            template += "</td>"
            #if self._get_service_records_row_cols_after(service_id,line):
                #template += self._get_service_records_row_cols_after(service_id,line)
        return template
    # -------------------------------------------
    # Custom html generation for record page
    # -------------------------------------------
    """
    =================================================================================
        Generate HTML for individual record page 
    =================================================================================
    """
    def portal_hr_service_record_dyanmic_page_template(self,service_id,record_id):
        m2m_ids = False
        fields = ''
        template = ''
            
        
        domain = [('id', '=', record_id.id)]
        record = request.env[service_id.header_model_id.model].search(domain)
        
        # find editable record
        domain_filter = ''
        if service_id.condition:
            domain_filter = safe_eval.safe_eval(service_id.condition)
        record_editable = False
        if record.filtered_domain(domain_filter):
            record_editable = True
        else:
            record_editable = False
            
            
        template += "<div class='row mb-4'>"
        
        for header in service_id.hr_service_items:
            
            template += "<div class='col-12 col-md-6 mb-1'>"
            template += "<strong>" + header.field_label + ": </strong>"
            
            if header.field_type == 'many2one':
                template += "<span>" + str(record[eval("'" + header.sudo().field_name + "'")].sudo().name) + "</span>"
            elif header.field_type == 'many2many':
                m2m_ids = request.env[header.field_model].sudo().search([('id','in',record[eval("'" + header.field_name + "'")].ids)])
                    #if m2m_ids.check_access_rights('read', raise_exception=False) else 0
                m2m_text = ''
                for m2m in m2m_ids:
                    m2m_text += m2m.name + ','
                template += "<span>" + m2m_text[:-1] + "</span>"
            elif header.field_type == 'selection':
                sel_id = request.env['ir.model.fields.selection'].sudo().search([('field_id','=',header.field_id.id),('value','=',record[eval("'" + header.field_name + "'")])],limit=1)
                if sel_id:
                    template += "<span>" + str(sel_id.name) + "</span>"
            else:
                template += "<span>" + str(record[eval("'" + header.field_name + "'")]) + "</span>"
            template += "</div>"
        template += "</div>"
        
        
        # line items
        counter = 0
        m2m_text = ''
        #template += "<h1>" + str(record_id.id) + record_id.name + "</h1>"
        
        #domain = [(service_id.parent_relational_field_id.name, '=', record_id.id)]
        domain = []
        # radio_options = [    {'value': 'excel', 'label': 'Excel'},    {'value': 'csv', 'label': 'CSV'},]
        record_liens = False
        if service_id.hr_service_record_line:
            for rec_line in service_id.hr_service_record_line:
                domain = [(rec_line.parent_relational_field_id.name, '=', record_id.id)]
                if rec_line.relational_field_id:
                    record_lines = request.env[rec_line.line_model_id.model].search(domain)
            
                
                # template += '<link href="https://cdn.datatables.net/1.13.1/css/jquery.dataTables.min.css" rel="stylesheet" />'
                # template += '<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>'
                # template += '<script type="text/javascript" src="https://cdn.datatables.net/1.13.1/js/jquery.dataTables.min.js"></script>'
                # template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/items_datatable.js"></script>'

                template += '<link href="/de_portal_hr_service/static/src/datatable.css" rel="stylesheet" />'
                template += '<link href="/de_portal_hr_service/static/src/datatable_export_button.css" rel="stylesheet" />'
                
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/jquery.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/datatable.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_buttons.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_jszip.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_pdfmake.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_vfs_fonts.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_btn_html5.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_print.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/js_export/datatable_select.js"></script>'

                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/items_datatable.js"></script>'
                template += '<script type="text/javascript" src="/de_portal_hr_service/static/src/js/sweetalert.js"></script>'

                
                template += "<section id='details' style='page-break-inside: auto; overflow:scroll;' class='mt32'>"
                template += "<table class='itemsTable table table-sm'>"
                template += "<thead class='bg-100'>"
        
                for label in rec_line.hr_service_record_line_items:
                    template += "<th>" + label.field_label + "</th>"
        
                template += "<th></th>"
                template += "</thead>"
        
                template += "<tbody class='sale_tbody'>"
            
                for line in record_lines:
                    counter += 1
                    if counter % 2 == 0:
                        template += "<tr class='bg-200'>"
                    else:
                        template += "<tr>"
                
                    for f in rec_line.hr_service_record_line_items:    
                        fields += f.field_name + ','
                        template += "<td>"
                        #template += eval("'" + f.field_name + "'")
                        
                        if line[eval("'" + f.field_name + "'")]:
                            if f.field_type == 'many2one':
                                if f.field_model == 'ir.attachment':
                                    template += "<a href='/web/content/" + str(line[eval("'" + f.field_name + "'")].id) + "?download=true' title='Dowload'><i class='fa fa-download'></i></a>"
                                else:
                                    template += str(line[eval("'" + f.field_name + "'")].name) \
                                        if line[eval("'" + f.field_name + "'")].check_access_rights('read', raise_exception=False) else 0

                            elif f.field_type == 'many2many':
                                m2m_ids = request.env[f.field_model].sudo().search([('id','in',line[eval("'" + f.field_name + "'")].ids)])
                                #if m2m_ids.check_access_rights('read', raise_exception=False) else 0
                                m2m_text = ''
                                for m2m in m2m_ids:
                                    m2m_text += m2m.name + ','
                                template += m2m_text[:-1]
                                #template += str(line[eval("'" + f.field_name + "'")].ids)
                            elif f.field_type == 'selection':
                                sel_id = request.env['ir.model.fields.selection'].sudo().search([('field_id','=',f.field_id.id),('value','=',line[eval("'" + f.field_name + "'")])],limit=1)
                                if sel_id:
                                    template += str(sel_id.name)
                            else:
                                template += str(line[eval("'" + f.field_name + "'")])
                        template += "</td>"
                
                
                    # add Edit delete button
                    template += '<td class="text-right">'
                    if service_id.is_edit and record_editable:
                        template += '<a href="/my/model/record/' + str(service_id.id) + '/' + str(rec_line.line_model_id.id) + '/' + str(line.id) + '/1' + '"><i class="fa fa-edit"></i></a>'
                        template += '<span style="padding-right:5px;padding-left:5px;"></span>'
                        template += '<a href="/my/model/record/' + str(service_id.id) + '/' + str(rec_line.line_model_id.id) + '/' + str(line.id) + '/delete"><i class="fa fa-trash"></i></a>'
                    template += '</td>'
                
                    template += "</tr>"
                
                fields = fields[:-1]
            
                template += "</tbody></table>"
                template +="</section>"
                if service_id.is_create and record_editable:
                    template +=  "<a href='/my/model/record/" + str(service_id.id) + "/" + str(rec_line.line_model_id.id) + "/" + str(record.id) + "/0" + "' >Add a record" + "</a>"
               
                # if service_id.allow_import:
                if rec_line.allow_import  and record_editable:
                    service = str(service_id.id)
                    model = str(rec_line.line_model_id.id)
                    record = str(record.id)
                    import_record = service + '-' + model + '-' + record
                    template += "<hr class='mt-4 mb-4'>"

                    template += "<input type='hidden' name='" + import_record + "' id='import_record' class='form-control' >"
                    
                    
                    template += "<div class='card-header mt-5'>"
                    template += "<div class='row no-gutters'>"
                    
                    template += "<div class='col-4'>"
                    template += "<span class='col-12 text-truncate bold'><b>Import Records</b></span>"
                    template += "<div class='col-12 text-left'>"
                    template += "<span>You can choose one of the following options:</span>"
                    template += "</div>"
                    template += "<div class='col-12'>"
                    radio_options = [{'value': 'excel', 'label': 'Excel'}, {'value': 'csv', 'label': 'CSV'}]
                    for radio_option in radio_options:
                        template += "<input type='radio'  name='file_format' value='" + radio_option['value'] + "' checked="+ radio_option['value'] + '==' + 'excel' + " />"
                        template += "&nbsp;<label>" + radio_option['label'] + "</label>"
                        template += "&nbsp;&nbsp;&nbsp;"
                    template += "</div>"

                    template += "</div>"

                  
                    

                    template += "<div class='col-4 col-md-4'>"
                    template += "<div class='col-12 col-md-12'>"
                    template += "<input type='file'  id='attached_document' class='form-control form-control-md' name='attached_document' multiple='1' />"
                    template += "</div>"
                    template += "<div class='col-12 col-md-12'>"
                    template += '<a href="/download/sample/import/record/' + str(service_id.id) + '/' + str(rec_line.id) + '"><i class="fa fa-download  btn-lg"></i>Download Example</a>'          
                    template += "</div>"
                    template += "</div>"
                    
                    template += "<div class='col-4 col-md-4'>"
                    template += '<button type="submit" class="btn btn-primary" onclick=submit_document();>Import Records</button>'    
                    template += "</div>"     
                    
                    
                    # template += "</div>"
                    template += "</div>"
                    template += "</div>"      

        return template
    
    