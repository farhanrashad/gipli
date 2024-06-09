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

        service_id = request.env['hr.service'].sudo().search([('id','=',service_id)],limit=1)
        # Assuming you have the group ID
        group_id = service_id.group_id.id  # Replace with your group ID
        # Check if the user belongs to the group using the group ID
        user = request.env.user
        user_groups = user.groups_id.ids  # This will give you a list of group IDs the user belongs to
        if group_id not in user_groups:
            # If the user doesn't belong to the group, redirect them to another page (e.g., the home page)
            return request.redirect('/my')
            
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
        #if access_token:
        Record = Record.sudo()
        
        line_item = request.env['hr.service.record.line'].search([('hr_service_id','=',service_id),('line_model_id','=',int(model_id))],limit=1)

        # find the model record
        if service_sudo.header_model_id.id == model_id:
            record_sudo = Record.search([('id', '=', record_id)], limit=1).sudo()
        elif line_item.line_model_id.id == model_id:
            record_sudo = Record.search([('id', '=', record_id)], limit=1).sudo()
        #task_sudo.attachment_ids.generate_access_token()

        

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

        # Assuming you have the group ID
        group_id = service_sudo.group_id.id  # Replace with your group ID
        # Check if the user belongs to the group using the group ID
        user = request.env.user
        user_groups = user.groups_id.ids  # This will give you a list of group IDs the user belongs to
        if group_id not in user_groups:
            # If the user doesn't belong to the group, redirect them to another page (e.g., the home page)
            return request.redirect('/my')
            
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
            #record_sudo.message_subscribe([partner_id.id])
        except Exception as e:
            print(e)

        access_token = ''
        try:
            access_token = record_sudo.access_token
        except:
            access_token = ''

    #   values['record_id']['expense_line_ids'][1]        
        values.update({
            'portal_hr_service_record_dyanmic_page_template': self.portal_hr_service_record_dyanmic_page_template(service_sudo,record_sudo),
            'record_id': record_sudo,
            'access_token': access_token,
            'title': record_title.upper(),
            'state': record_state, #record_state.upper(),
            'record_editable': record_editable,
            'allow_messages': service_sudo.allow_messages,
            'allow_log_note': service_sudo.allow_log_note,
            'show_attachment': service_sudo.show_attachment,
        })
        #if hasattr(record_sudo, 'access_token'):
        #    values.update({
        #        'access_token': record_sudo.access_token,
        #    })
        
        if service_sudo.allow_log_note:
            values.update({
                'portal_hr_service_record_log_notes': self.portal_hr_service_record_log_notes(service_sudo,model_id, record_sudo)
            })

        if not record_sudo:
            return request.redirect('/my')

        return request.render("de_portal_hr_service.portal_my_hr_service_record", values)

    
    # -------------------------------------------
    # Custom html generation
    # -------------------------------------------
    def _get_portal_my_entries_content(self,entries):
        template = ''
        # Dynamic Header
        for entry in entries:
            template += '<strong>' + str(entry.name) + '</strong><br/>'

    # -------------------------------------------------------------
    # Custom html generation for log Notes
    # -------------------------------------------------------------
    def portal_hr_service_record_log_notes(self,service_id, model_id, record_id):
        log_output = ''
        log_output += '<div id="discussion" class="mt32">'
        messages = service_id._get_log_notes(record_id)
        for message in messages:
            user_avatar_url = f"/web/image/res.partner/{message.author_id.id}/avatar_128"


            log_output += '<div class="o_portal_chatter_messages">'
            log_output += '<div id="message-"' + str(message.id) + 'class="d-flex o_portal_chatter_message" style="display:inline-block;vertical-align:top;">'
            log_output += f'<img class="o_portal_chatter_avatar" width="45" height="45" src="{user_avatar_url}" alt="Avatar" style="margin-right:1rem;"/>'
            #output += f'<img class="o_portal_chatter_avatar" width="45" height="45" t-attf-src="data:image/png;base64,{message.author_avatar}" alt="Avatar" style="margin-right:1rem;"/>'
            #output += '<img t-att-src="data:image/png;base64,' + str(message.author_id.avatar_128)[2:-1] + '"/>'
            
            log_output += '</div>'

            log_output += '<div class="flex-grow-1" style="display:inline-block;width:90%;">'
            log_output += '<div class="o_portal_chatter_message_title">'
            log_output += f'<h5 class="mb-1">{message.author_id.display_name}</h5>'
            log_output += f'<p class="o_portal_chatter_published_date" style="font-size:85%;color:#6C757D;margin:0px;">Published On {message.date}</p>'
            log_output += '</div>'
            log_output += f'<p>{message.body}</p>'

            log_output += '''
            <div class="container">        
                <div class="row">
            '''
            for attach in message.attachment_ids:
                log_output += '''
                <div class="col-lg-2 col-md-3 col-sm-6">
                    <div class=" mb-2 position-relative text-center" data-id="1287">
                        <a href="/attachment/download?attachment_id={attach_id}" >
                            <span t-esc="attach_id" class="fa fa-download">
                                {attach_name}
                            </span>
                        </a>
                    </div>
                </div>
            '''.format(attach_id=attach.id, attach_name=attach.name)
            log_output += '''        
                </div>
            </div>
            '''
            
            log_output += '</div>'

            
            log_output += '</div>'
        log_output += '</div>'

        # ------ Messages output -------------------
        msg_output = ''
        msg_output += '<div id="discussion" class="mt32">'
        messages = service_id._get_messages(record_id)
        for message in messages:
            user_avatar_url = f"/web/image/res.partner/{message.author_id.id}/avatar_128"


            msg_output += '<div class="o_portal_chatter_messages">'
            msg_output += '<div id="message-"' + str(message.id) + 'class="d-flex o_portal_chatter_message" style="display:inline-block;vertical-align:top;">'
            msg_output += f'<img class="o_portal_chatter_avatar" width="45" height="45" src="{user_avatar_url}" alt="Avatar" style="margin-right:1rem;"/>'
            #output += f'<img class="o_portal_chatter_avatar" width="45" height="45" t-attf-src="data:image/png;base64,{message.author_avatar}" alt="Avatar" style="margin-right:1rem;"/>'
            #output += '<img t-att-src="data:image/png;base64,' + str(message.author_id.avatar_128)[2:-1] + '"/>'
            
            msg_output += '</div>'

            msg_output += '<div class="flex-grow-1" style="display:inline-block;width:90%;">'
            msg_output += '<div class="o_portal_chatter_message_title">'
            msg_output += f'<h5 class="mb-1">{message.author_id.display_name}</h5>'
            msg_output += f'<p class="o_portal_chatter_published_date" style="font-size:85%;color:#6C757D;margin:0px;">Published On {message.date}</p>'
            msg_output += '</div>'
            msg_output += f'<p>{message.body}</p>'

            
            msg_output += '''
            <div class="container">        
                <div class="row">
            '''
            for attach in message.attachment_ids:
                msg_output += '''
                <div class="col-lg-2 col-md-3 col-sm-6">
                    <div class=" mb-2 position-relative text-center" data-id="1287">
                    <a href="/attachment/download?attachment_id={attach_id}">
                        <span t-esc="attach_id" class="fa fa-download">
                            {attach_name}
                        </span>
                    </a>
                    </div>
                </div>
            '''.format(attach_id=attach.id, attach_name=attach.name)
            msg_output += '''        
                </div>
            </div>
            '''
            
            msg_output += '</div>'
            msg_output += '</div>'
        msg_output += '</div>'

        
        # ----------- Attachments ----------------
        attach_output = ''
        attachments = service_id._get_attachments(record_id)
        attach_output += '''
        <div class="o_portal_chatter_attachments mt32">        
            <div class="row">
        '''             
        for attach in attachments:
            attach_output += '''
                <div class="col-lg-2 col-md-3 col-sm-6">
                    <div class="o_portal_chatter_attachment mb-2 position-relative text-left" data-id="1287">
                    <a href="/attachment/download?attachment_id={attach_id}">
                        <span t-esc="attach_id" class="fa fa-download">
                            {attach_name}
                        </span>
                    </a>
                    </div>
                </div>
            '''.format(attach_id=attach.id, attach_name=attach.name)
        attach_output += '''        
            </div>
        </div>
        '''
        # ----------- Message form ---------------
        user_avatar = f"/web/image/res.partner/{request.env.user.partner_id.id}/avatar_128"
        form_html = '''
        <form 
                    action="/my/message/{service_id}/{model_id}/{record_id}" 
                    method="post" enctype="multipart/form-data" 
                    class="o_mark_required row" 
                    data-mark="*" data-success-page=""
                    t-att-id="'form' + str(service_id.id)"
                >

    <input type="hidden" class="form-control s_website_form_input" id="service_id" name="service_id" t-att-value="{service_id}" />
                            <input type="hidden" class="form-control s_website_form_input" id="model_id" name="model_id" t-att-value="{model_id}" />
                            <input type="hidden" class="form-control s_website_form_input" id="record_id" name="record_id" t-att-value="{record_id}" />
                            
    <div class="o_portal_chatter_composer">
        <div class="o_portal_chatter_composer">
            <div class="alert alert-danger mb8 d-none o_portal_chatter_composer_error" role="alert">
                Oops! Something went wrong. Try to reload the page and log in.
            </div>
            <div class="d-flex">
                <img alt="Avatar" width="45" height="45" class="o_portal_chatter_avatar o_object_fit_cover align-self-start mr16" src="{user_avatar}">
                <div class="flex-grow-1">
                    <div class="o_portal_chatter_composer_input">
                        <div class="o_portal_chatter_composer_body mb32">
                            <textarea rows="4" name="message" class="form-control" required="1" placeholder="Write a message..."></textarea>
                            <div class="o_portal_chatter_attachments mt-3"></div>
                            <div class="mt8">
                                <button data-action="/mail/chatter_post" class="o_portal_chatter_composer_btn btn btn-primary" type="submit">Send</button>
                                <input class="file" id="attachments" type="file" name="attachments" multiple="true" data-show-upload="true" data-show-caption="true" accept="image/*,application/pdf,video/*" />                            
                            </div>
                        </div>
                    </div>
                    <div class="d-none">
                        <input type="file" class="o_portal_chatter_file_input" multiple="multiple">
                        
                    </div>
                </div>
            </div>
        </div>
    </div>
    </form>
    '''.format(service_id=service_id.id, model_id=model_id, record_id=record_id.id, user_avatar=user_avatar)

        # -------------------- Generate Output -----------------------------
    
        output = ''
        messages_tab_link = ''
        messages_tab_html = ''
        logs_tab_link = ''
        logs_tab_html = ''
        attach_tab_link = ''
        attach_tab_html = ''
        
        if service_id.allow_messages:
            messages_tab_link = '''
                <li class="nav-item">
                    <a class="nav-link active" id="messages-tab" data-toggle="tab" href="#messages" role="tab" aria-controls="messages">Messages</a>
                </li>    
            '''
            messages_tab_html = '''
            <div class="tab-pane fade show active" id="messages" role="tabpanel" aria-labelledby="messages-tab">
                {msg_output}
                {form_html}
            </div>
            '''.format(msg_output=msg_output, form_html=form_html)
                    
        if service_id.allow_log_note:
            logs_tab_link = '''
            <li class="nav-item">
                <a class="nav-link" id="logs-tab" data-toggle="tab" href="#logs" role="tab" aria-controls="logs">Logs</a>
            </li>
            '''
            logs_tab_html = '''
            <div class="tab-pane fade" id="logs" role="tabpanel" aria-labelledby="logs-tab">
                {log_output}
            </div>
            '''.format(log_output=log_output)
                        
        if service_id.show_attachment:
            attach_tab_link = '''
            <li class="nav-item">
                <a class="nav-link" id="attach-tab" data-toggle="tab" href="#attach" role="tab" aria-controls="attach" aria-selected="">Attachments</a>
            </li>
            '''
            attach_tab_html = '''
            <div class="tab-pane fade" id="attach" role="tabpanel" aria-labelledby="attach-tab">
                {attach_output}
            </div>
            '''.format(attach_output=attach_output)
                    
        output = '''
        <div class="mt-4">
            <ul class="nav nav-tabs" id="myTab" role="tablist">
                {messages_tab_link}
                {logs_tab_link}
                {attach_tab_link}
            </ul>
            <div class="tab-content" id="myTabContent">
                {messages_tab_html}
                {logs_tab_html}
                {attach_tab_html}
            </div>
        </div>
        '''.format(
            messages_tab_link=messages_tab_link, messages_tab_html=messages_tab_html,
            logs_tab_link=logs_tab_link, logs_tab_html=logs_tab_html,
            attach_tab_link=attach_tab_link, attach_tab_html=attach_tab_html
        )
        
        return output



        
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
        #message_partner_ids = request.env['ir.model.fields'].sudo().search([('name','=','message_partner_ids'),('model','=',service_id.header_model_id.model)],limit=1)
        
        employee_id = request.env['ir.model.fields'].sudo().search([('name','=','employee_id'),('model','=',service_id.header_model_id.model)],limit=1)
        
        partner_id = request.env['ir.model.fields'].sudo().search([('name','=','partner_id'),('model','=',service_id.header_model_id.model)],limit=1)
        
        records = request.env[service_id.header_model_id.model].sudo().browse(service_id._get_records_filter_by_domain(request.env.user.partner_id.id))


      
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

        template += '<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>'
        template += '<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>'
        template += '<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>'
        
        domain = [('id', '=', record_id.id)]
        record = record_id #request.env[service_id.header_model_id.model].search(domain)

        #raise UserError(str(record_id))
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
                if header.field_model == 'ir.attachment':

                    template += '''
                        <a href="/attachment/download?attachment_id={attach_id}">
                            <span t-esc="attach_id" class="fa fa-download">
                                {attach_name}
                            </span>
                        </a>
                    '''.format(attach_id=record[eval("'" + header.field_name + "'")].id, attach_name=header.field_name)
                    
                else:
                    template += str(record[eval("'" + header.field_name + "'")].name) \
                        if record[eval("'" + header.field_name + "'")].check_access_rights('read', raise_exception=False) else ''

                
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
        m2m_text = ''
        domain = []
        if service_id.hr_service_record_line:
            for rec_line in service_id.hr_service_record_line:

                model_name = rec_line.line_model_id.name
                
                template += "<h4  class='mx-auto mt-3'>"+ model_name +"</h4>"


                template += "<section id='details' style='page-break-inside: auto; overflow:scroll;' class='mt32'>"
                template += "<table class='itemsTable table table-sm'>"
                template += "<thead class='bg-100'>"
                
                domain = [(rec_line.parent_relational_field_id.name, '=', record_id.id)]
                
                if rec_line.relational_field_id:
                    record_lines = request.env[rec_line.line_model_id.model].search(domain)
                    
                for label in rec_line.hr_service_record_line_items:
                    template += "<th>" + label.field_label + "</th>"
        
                template += "<th></th>"
                template += "</thead>"
                
                template += "<tbody class='sale_tbody'>"
                # ------- display record line items -----------
                for line in record_lines:
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
                                        if line[eval("'" + f.field_name + "'")].check_access_rights('read', raise_exception=False) else ''

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
                    
                template += "</tbody>"
                
                template += "</table>"
                if service_id.is_create and record_editable:

                    template +=  "<a href='/my/model/record/" + str(service_id.id) + "/" + str(rec_line.line_model_id.id) + "/" + str(record.id) + "/0" + "' >Add a record" + "</a>"
                    
                    
                # if service_id.allow_import:
                if rec_line.allow_import and record_editable:
                    service = str(service_id.id)
                    model = str(rec_line.line_model_id.id)
                    import_record_id = str(record.id)
                    rec_line_id = str(rec_line.id)

                    import_record = service + '-' + model + '-' + import_record_id + '-' + rec_line_id
                    
                    template += "<hr class='mt-4 mb-4'>"

                    template += "<input type='hidden' name='import_record' id='" + import_record + "' class='form-control' >"
                    # template += "<input type='hidden' name='" + import_record + "' id='import_record' class='form-control' >"
                    
                    
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
                    attachement_record_line_id = "attached_document_" + str(rec_line.id)
                    template += "<input type='file'  id='" + attachement_record_line_id + "' class='form-control form-control-md' name='attached_document' multiple='1' />"
                    template += "<input type='hidden'  id='" + str(rec_line.id) + "' class='form-control form-control-md' name='record_line_id'/>"
                    template += "</div>"
                    template += "<div class='col-12 col-md-12'>"
                    template += '<a href="/download/sample/import/record/' + str(service_id.id) + '/' + str(rec_line.id) + '"><i class="fa fa-download  btn-lg"></i>Download Example</a>'          
                    template += "</div>"
                    template += "</div>"
                    
                    template += "<div class='col-4 col-md-4'>"
                    template += '<button type="button" class="btn btn-primary"  onclick=submit_document();>Import Records</button>'    
                    # template += '<button type="submit" class="btn btn-primary"  t-attf-onclick="submit_document( {{rec_line.id}} );">Import Records</button>'    
                    template += "</div>"     
                    
                    
                    # template += "</div>"
                    template += "</div>"
                    template += "</div>" 
                    
                    
                    
                template += "</section>"
                
                

        return template
    
    