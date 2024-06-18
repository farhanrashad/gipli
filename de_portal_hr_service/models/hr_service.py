# -*- coding: utf-8 -*-

import base64
import ast
import json
import re

from odoo import api, fields, models, tools, _
from random import randint
from odoo.exceptions import UserError
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _
from odoo.tools import safe_eval
from odoo.exceptions import ValidationError

from lxml import etree

from odoo.osv import expression


class HRService(models.Model):
    _name = 'hr.service'
    _description = 'HR Self Service'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'id'
    
    
    READONLY_STATES = {
        'validate': [('readonly', True)],
        'publish': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    name = fields.Char(string='Name', required=True, translate=True, states=READONLY_STATES,)
    active = fields.Boolean(default=True)
    description = fields.Char(string='Description')    
    
    header_model_id = fields.Many2one('ir.model', ondelete='cascade', string='Model', states=READONLY_STATES, required=True)
    header_model_name = fields.Char(related='header_model_id.model', string='Model Name')
    filter_domain = fields.Char(string='Domain', help="If present, this domain would apply to filter records.")
    condition = fields.Char(string='Condition', help="If present, this condition must be satisfied for operations.")
    title_field_id = fields.Many2one('ir.model.fields', string='Title Field', ondelete="cascade", states=READONLY_STATES,)
    state_field_id = fields.Many2one('ir.model.fields', string='State Field', ondelete="cascade", states=READONLY_STATES,)
    filter_field_id = fields.Many2one('ir.model.fields', string='Filter By ',ondelete="cascade")

    sequence = fields.Integer('Sequence', default=0)
    is_create = fields.Boolean(string='Create', help='Allow record creation', states=READONLY_STATES,)
    is_edit = fields.Boolean(string='Edit', help='Allow record edition', states=READONLY_STATES,)
    allow_messages = fields.Boolean(string='Allow Messages', store=True, compute='_compute_allow_messages', readonly=False, states=READONLY_STATES, help='Allow messages to user on portal')

    allow_log_note = fields.Boolean(string='Allow Log Note', store=True, compute='_compute_allow_log_note', readonly=False, states=READONLY_STATES, help='Allow Log Note to user on portal')

    show_attachment = fields.Boolean(string='Show Attachments', store=True, compute='_compute_show_attachment', readonly=False, states=READONLY_STATES, help='show attachment on portal')

    show_activities = fields.Boolean(string='Show Activities', store=True, compute='_compute_show_activities', readonly=False, states=READONLY_STATES, help='show activities on portal')

    
    @api.onchange('allow_messages')
    def _onchange_allow_messages(self):
        partner_id = self.env.user.partner_id
        if self.allow_messages and partner_id and self.id and self.id.origin:
            self.message_subscribe([partner_id.id])
        elif not self.allow_messages and partner_id:
            self.message_unsubscribe([partner_id.id])    


    group_id = fields.Many2one('res.groups', string='Group')
    
    hr_service_items = fields.One2many('hr.service.items', 'hr_service_id', string='Service Items', copy=True, auto_join=True, states=READONLY_STATES,)
    
    hr_service_record_line = fields.One2many('hr.service.record.line', 'hr_service_id', string='Record Lines', copy=True, auto_join=True, states=READONLY_STATES,)

    
    # access_group_id = fields.Many2one( string='Group',comodel_name='res.groups',ondelete='restrict')
    
    
    field_variant_id = fields.Many2one(string='Field Variant', comodel_name='hr.service.field.variant')
    

    state = fields.Selection([
        ('draft', 'New'),
        ('validate', 'Validate'),
        ('publish', 'Publish'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
    
    def button_draft(self):
        self.write({'state': 'draft'})
        return {}
    
    def button_cancel(self):
        self.write({'state': 'cancel'})
        return {}
    
    def button_validate(self):

        # Test Values
        non_exp_field_ids = self.hr_service_items.filtered(lambda x: not x.change_field_exp)
        exp_field_ids = self.hr_service_items.filtered(lambda x: x.change_field_exp)

        for field in exp_field_ids:
            # Extract field names from the expression
            expression = field.change_field_exp
            field_names = re.findall(r'\b\w+\b(?=\.)', expression)            
            # Filter the service items based on the extracted field names
            matching_fields = self.hr_service_items.filtered(lambda x: x.field_name in field_names)
            for f in matching_fields:
                f.ref_changeable_field_ids = [(4, field.field_id.id)]        
        self.write({'state': 'validate'})
    
    def button_publish(self):
        field_model_ids = self.env['ir.model']
        #model_ids = self.env['ir.model']
        self_model_ids = self.env['ir.model'].search([('model','in',['hr.service.field.variant','hr.service.field.variant.line'])])
        model_ids = self.header_model_id + self.hr_service_record_line.mapped('line_model_id') + self_model_ids
        
        field_model_ids += self.env['ir.model'].search([('model', 'in', self.hr_service_items.filtered(lambda x: x.field_model != False).mapped('field_model'))])
        field_model_ids += self.env['ir.model'].search([('model', 'in', self.hr_service_record_line.hr_service_record_line_items.filtered(lambda x: x.field_model != False).mapped('field_model'))])

        #for line in self.hr_service_items:
        #    if line.field_model:
        #        model_ids = self.env['ir.model'].search([('model','=',line.field_model)],limit=1)
                
        
        #+ self.hr_service_items_line.field_model
        
        group_id = self.env['res.groups']
        ima_id = self.env['ir.model.access']
        field_ima_id = self.env['ir.model.access']
        
        vals = {}
        group_id = self.env['res.groups'].search([('name', '=', 'Portal')],limit=1)
        for model in model_ids:
            ima_id = self.env['ir.model.access'].search([('model_id','=',model.id),('group_id','=',group_id.id)],limit=1)
            vals = ({
                'name': group_id.name + ' :- ' + model.name,
                'model_id': model.id,
                'group_id': group_id.id,
                'perm_read': True,
                'perm_write': True, 
                'perm_create': True,
                'perm_unlink': True,
                'active': True,
            })
            if not ima_id or len(ima_id) == 0:
                self.env['ir.model.access'].sudo().create(vals)
            else:
                ima_id.sudo().write(vals)

        # Give Permission to base models Product Template, Product, Partner
        base_model_ids = self.env['ir.model'].search([('model','in',['product.template','product.product','res.partner'])])
        
        for model in (field_model_ids + base_model_ids):
            field_ima_id = self.env['ir.model.access'].search([('model_id','=',model.id),('group_id','=',group_id.id)],limit=1)
            vals = ({
                'name': group_id.name + ' :- ' + model.name,
                'model_id': model.id,
                'group_id': group_id.id,
                'perm_read': True,
                'perm_write': False, 
                'perm_create': False,
                'perm_unlink': False,
                'active': True,
            })
            if not field_ima_id or len(field_ima_id) == 0:
                self.env['ir.model.access'].sudo().create(vals)
            else:
               field_ima_id.sudo().write(vals) 

        
                
        #raise UserError(_(vals))
        self.write({'state': 'publish'})

        if self.show_activities:
            self._compute_show_activities()

        if self.allow_messages:
            self._compute_allow_messages()

        if self.allow_log_note:
            self._compute_allow_log_note()

        if self.show_attachment:
            self._compute_show_attachment()
            
        return {}

    
        
    
    
    @api.depends('header_model_id')
    def _compute_allow_messages(self):
        records = 0
        for service in self:
            service.allow_messages = False            
            records = self.env['ir.model.fields'].search_count([
                ('model_id','=',service.header_model_id.id),
                ('relation','=','mail.message')
            ],limit=1)
            if records:
                service.allow_messages = True

    @api.depends('header_model_id')
    def _compute_allow_log_note(self):
        records = 0
        for service in self:
            service.allow_log_note = False
            
            records = self.env['ir.model.fields'].search_count([
                ('model_id','=',service.header_model_id.id),
                ('relation','=','mail.message')
            ],limit=1)
            if records:
                service.allow_log_note = True

    @api.depends('header_model_id')
    def _compute_show_attachment(self):
        records = 0
        for service in self:
            service.show_attachment = False
            records = self.env['ir.model.fields'].search_count([
                ('model_id','=',service.header_model_id.id),
                ('relation','=','mail.message')
            ],limit=1)
            if records:
                service.show_attachment = True

    @api.depends('header_model_id')
    def _compute_show_activities(self):
        for record in self:
            field = self.env['ir.model.fields'].search([
                ('model_id','=',record.header_model_id.id),
                ('relation','=', 'mail.activity'),
            ],limit=1)
            if field:
                record.show_activities = True
            else:
                record.show_activities = False

    def get_record_count(self, user_id):
        domain = []
        domain += expression.AND([self._get_user_domain(user_id.partner_id.id), self._get_filter_domain()])
        records = self.env[self.header_model_id.model].search_count(domain)
        return records

    def _get_records_search_by_domain(self,domain):
        records = self.env[self.header_model_id.model].search(domain).ids
        return records
        
    def _get_records_filter_by_domain(self,partner_id):
        domain = []
        domain += expression.AND([self._get_user_domain(partner_id), self._get_filter_domain()])
        records = self.env[self.header_model_id.model].search(domain).ids
        return records

    def _get_user_domain(self,partner_id):
        user_domain = []
        if self.filter_field_id:
            user_domain =  [(self.filter_field_id.name, 'in', [partner_id]),(self.filter_field_id.name, '=', partner_id)]
        return user_domain

    def _get_filter_domain(self):
        filter_domain = []
        if self.filter_domain:
            filter_domain = safe_eval.safe_eval(self.filter_domain)
        return filter_domain
        

    def _get_log_notes(self, record_id):
        message_ids = self.env['mail.message'].search([
            ('res_id','=',record_id.id),
            ('model','=',self.header_model_id.model),
            ('subtype_id','=',self.env.ref('mail.mt_note').id)
        ])
        return message_ids

    def _get_messages(self, record_id):
        message_ids = self.env['mail.message'].search([
            ('res_id','=',record_id.id),
            ('model','=',self.header_model_id.model),
            ('subtype_id','=',self.env.ref('mail.mt_comment').id)
        ])
        return message_ids

    def _get_attachments(self, record_id):
        attachment_ids = self.env['ir.attachment'].search([
            ('res_id','=',record_id.id),
            ('res_model','=',self.header_model_id.model),
        ])
        return attachment_ids

    def _get_activities(self, record_id):
        for record in self:
            field = self.env['ir.model.fields'].search([
                ('model_id','=',record.header_model_id.id),
                ('relation','=', 'mail.activity'),
            ],limit=1)
            activities = record_id[field.name]
            return activities

    #def get_field_value_from_expression(self, model_id, field_model, field_name, field_value, changeable_field_name):
    def get_field_value_from_expression(self,model_id,changeable_field_ids):
        model = self.env['ir.model'].browse(model_id)
        record = self.env[field_model].browse(field_value)
        if self.header_model_id.id == model_id:
            field = self.env['hr.service.items'].search([('field_name','=',changeable_field_name)])
            #if cf.change_field_exp
            value = 100
        else:
            for lm in self.hr_service_record_line:
                if lm.line_model_id.id == model_id:
                    value = 50
        return value


    def _get_default_field_values(self, form_elements_json, changeable_field_ids, field_name):
        form_elements = json.loads(form_elements_json)

        service_id = 0
        model_id = 0
        record_id = 0
        
        for element in form_elements:
            if element['name'] == 'service_id':
                service_id = element['value']
            elif element['name'] == 'model_id':
                model_id = element['value']
            elif element['name'] == 'record_id':
                record_id = element['value']

        model = self.env['ir.model'].browse(int(model_id))
        computed_field_values = {}

        eval_context = {}
        field_pattern = re.compile(r'(\w+\.\w+|\w+)')
        cf_values = []

        service = self.env['hr.service'].browse(service_id)
        
        if model.id == self.header_model_id.id:
            service_items = self.mapped('hr_service_items')
        else:
            service_items = self.hr_service_record_line.mapped('hr_service_record_line_items')

        for item in service_items:
            if item.change_field_exp:
                matches = field_pattern.findall(item.change_field_exp)
                if matches:
                    for match in matches:
                        if '.' in match:
                            f1, f2 = match.split('.')
                        else:
                            f1 = match
                            f2 = None

                        f1_value = next((element['value'] for element in form_elements if element['name'] == f1), None)
                        
                        if f1_value:
                            related_item = service_items.search([('field_name', '=', f1)],limit=1)
                            related_model = related_item.field_model
                            record = self.env[related_model].browse(int(f1_value))

                            eval_context[f1] = record
                            if f2:
                                eval_context[match] = getattr(record, f2)
                            else:
                                eval_context[f1] = record
                
                        cf_values.append({
                            'field1': f1,
                            'field1_value': f1_value,
                            'field2': f2,
                            'field2_value': record[f2],
                        })

                
                try:
                    # Evaluate the expression
                    result_value = eval(item.change_field_exp, {}, eval_context)
                    computed_field_values[item.field_name] = result_value
                except Exception as e:
                    computed_field_values[item.field_name] = 0
        
        field_values = {
            'computed_field_values': computed_field_values,
        }

        
        return field_values
            

    def _get_list_values(self, form_elements_json, field_name):
        form_elements = json.loads(form_elements_json)

        service_id = 0
        model_id = 0
        record_id = 0
        
        for element in form_elements:
            if element['name'] == 'service_id':
                service_id = element['value']
            elif element['name'] == 'model_id':
                model_id = element['value']
            elif element['name'] == 'record_id':
                record_id = element['value']

        model = self.env['ir.model'].browse(int(model_id))
        computed_list_values = {}

        eval_context = {}
        field_pattern = re.compile(r'(\w+\.\w+|\w+)')
        cf_values = []

        service = self.env['hr.service'].browse(int(service_id))
        
        if model.id == self.header_model_id.id:
            service_items = self.mapped('hr_service_items')
        else:
            service_items = self.hr_service_record_line.mapped('hr_service_record_line_items')
            
        list_ids = []
        source_record = 0
        list_values = {}
        
        for item in service_items.filtered(lambda x:x.populate_list_expr):
            if item.populate_list_expr:
                # Source fields
                list_ids = []
                source_field_item = service_items.search([('field_name', '=', field_name)],limit=1)
                source_field_model = source_field_item.field_model
                source_value = next((element['value'] for element in form_elements if element['name'] == field_name), None)
                source_record = self.env[source_field_model].browse(int(source_value))
                
        
                #Destinations
                dest_field_item = service_items.search([],limit=1)
                dest_field_model = dest_field_item.field_model
                
                
        
                populate_matches = field_pattern.findall(item.populate_list_expr)
        
                for match in populate_matches:
                    if '.' in match:
                        f1, f2 = match.split('.')
                        f1_model = self.env['ir.model.fields'].search([
                            ('model','=',source_field_model),
                            ('name','=',f1)
                        ],limit=1).relation
                        
                        dest_field_item = service_items.search([('field_model', '=', f1_model)],limit=1)
                        dest_field_model = dest_field_item.field_model
                        dest_field_id = self.env['ir.model.fields'].search([
                            ('model','=',source_field_model),
                            ('relation','=',dest_field_model),
                        ],limit=1)
                        list_ids = source_record[f1].mapped(f2).ids
                        dest_records = self.env[dest_field_model].search([(f2, 'in', list_ids)])
                    else:
                        f1 = match
                        f2 = None
                        dest_field_item = service_items.search([('field_model', '=', f1_model)],limit=1)
                        dest_field_model = dest_field_item.field_model
                        dest_field_id = self.env['ir.model.fields'].search([
                            ('model','=',source_field_model),
                            ('relation','=',dest_field_model),
                        ],limit=1)
                        list_ids = source_record[f1].ids
                        dest_records = self.env[dest_field_model].search([('id','in',tuple(list_ids))])
        
            for record in dest_records:
                list_values[record.name] = record.id

        

        computed_list_values = {
            dest_field_item.field_name: list_values,
        }

        
        return computed_list_values


    
        
    def get_changeable_field_values(self, form_elements_json, changeable_field_ids, field_name):
        # Process the form elements JSON data
        form_elements = json.loads(form_elements_json)

        service_id = 0
        model_id = 0
        record_id = 0
        
        for element in form_elements:
            if element['name'] == 'service_id':
                service_id = element['value']
            elif element['name'] == 'model_id':
                model_id = element['value']
            elif element['name'] == 'record_id':
                record_id = element['value']

        model = self.env['ir.model'].browse(int(model_id))
        computed_field_values = {}

        eval_context = {}
        field_pattern = re.compile(r'(\w+\.\w+|\w+)')
        # Find the changable field records
        cf_values = []

        service = self.env['hr.service'].browse(service_id)
        # service_items = self.env['hr.service.items']
        if model.id == self.header_model_id.id:
            service_items = self.mapped('hr_service_items')
        else:
            service_items = self.hr_service_record_line.mapped('hr_service_record_line_items')
        #    service_items = self.env['hr.service.items'].search([('field_id.id', 'in', changeable_field_ids)]) #.mapped('hr_service_items')
            # service_items = service_items.search([('field_id.id', 'in', changeable_field_ids)])
        #else:
        #    service_items = self.hr_service_record_line.mapped('hr_service_record_line_items')
        #    service_items = service_items.search([('field_id.id', 'in', changeable_field_ids)])
    
        #service_items = service_items.search([('field_id.id', 'in', changeable_field_ids)])

        
        for item in service_items:
            if item.change_field_exp:
                matches = field_pattern.findall(item.change_field_exp)
                if matches:
                    for match in matches:
                        if '.' in match:
                            f1, f2 = match.split('.')
                        else:
                            f1 = match
                            f2 = None

                        f1_value = next((element['value'] for element in form_elements if element['name'] == f1), None)
                        
                        if f1_value:
                            related_item = self.env['hr.service.items'].search([('field_name', '=', f1)],limit=1)
                            related_model = related_item.field_model
                            record = self.env[related_model].browse(int(f1_value))

                            eval_context[f1] = record
                            if f2:
                                eval_context[match] = getattr(record, f2)
                            else:
                                eval_context[f1] = record
                
                        cf_values.append({
                            'field1': f1,
                            'field1_value': f1_value,
                            'field2': f2,
                            'field2_value': record[f2],
                        })

                
                try:
                    # Evaluate the expression
                    result_value = eval(item.change_field_exp, {}, eval_context)
                    computed_field_values[item.field_name] = result_value
                except Exception as e:
                    computed_field_values[item.field_name] = 0
        

        # ================= list values ======================================
        if model.id == self.header_model_id.id:
            service_items = self.mapped('hr_service_items')
        else:
            service_items = self.hr_service_record_line.mapped('hr_service_record_line_items')
            
        list_ids = []
        source_record = 0
        list_values = {}
        
        for item in service_items.filtered(lambda x:x.populate_list_expr):
            if item.populate_list_expr:
                # Source fields
                list_ids = []
                source_field_item = service_items.search([('field_name', '=', field_name)],limit=1)
                source_field_model = source_field_item.field_model
                source_value = next((element['value'] for element in form_elements if element['name'] == field_name), None)
                source_record = self.env[related_model].browse(int(source_value))
                
        
                #Destinations
                dest_field_item = service_items.search([],limit=1)
                dest_field_model = dest_field_item.field_model
                
                
        
                populate_matches = field_pattern.findall(item.populate_list_expr)
        
                for match in populate_matches:
                    if '.' in match:
                        f1, f2 = match.split('.')
                        f1_model = self.env['ir.model.fields'].search([
                            ('model','=',source_field_model),
                            ('name','=',f1)
                        ],limit=1).relation
                        
                        dest_field_item = service_items.search([('field_model', '=', f1_model)],limit=1)
                        dest_field_model = dest_field_item.field_model
                        dest_field_id = self.env['ir.model.fields'].search([
                            ('model','=',source_field_model),
                            ('relation','=',dest_field_model),
                        ],limit=1)
                        list_ids = source_record[f1].mapped(f2).ids
                        dest_records = self.env[dest_field_model].search([(f2, 'in', list_ids)])
                    else:
                        f1 = match
                        f2 = None
                        dest_field_item = service_items.search([('field_model', '=', f1_model)],limit=1)
                        dest_field_model = dest_field_item.field_model
                        dest_field_id = self.env['ir.model.fields'].search([
                            ('model','=',source_field_model),
                            ('relation','=',dest_field_model),
                        ],limit=1)
                        list_ids = source_record[f1].ids
                        dest_records = self.env[dest_field_model].search([('id','in',tuple(list_ids))])
        
            for record in dest_records:
                list_values[record.name] = record.id

        

        changeable_field_values = {
            #'service_id': service_id,
            #'model_id': model_id,
            #'record_id': record_id,
            #'field_name': field_name,
            #'changeable_field_ids': changeable_field_ids,
            #'cf_values': cf_values,
            #'f1': dest_records,
            #'f2': f2,
            dest_field_item.field_name: list_values,
            'computed_field_values': computed_field_values,
        }

        
        return changeable_field_values

    def create_message(self, model, record, user, message, attachment_files=None, user_ids=None):
        attachment_ids = []
    
        if attachment_files:
            for attachment in attachment_files:
                attached_file = attachment.read()
                if attached_file:  # Ensure the attachment is not empty
                    attachment_id = self.env['ir.attachment'].sudo().create({
                        'name': attachment.filename,
                        'res_model': model.model,
                        'res_id': record.id,
                        'type': 'binary',
                        'datas': base64.b64encode(attached_file).decode('ascii'),
                    })
                    attachment_ids.append(attachment_id.id)

        # Create a linkable user list
        user_links = ''
        if user_ids:
            follower_ids = []
            for user_id in user_ids:
                user_rec = self.env['res.users'].sudo().browse(int(user_id))
                user_links += f'<a href="/web#model=res.partner&id={user_rec.partner_id.id}">{user_rec.partner_id.name}</a>, '
                follower_ids.append(user_rec.partner_id.id)
            
            # Remove the trailing comma and space
            if user_links:
                user_links = user_links[:-2]
            
            # Add users as followers of the document
            record.message_subscribe(partner_ids=follower_ids)
    
        # Add users to the message body
        if user_links:
            message = f'{user_links}<br/><br/>{message}'
        
        message_id = self.env['mail.message'].create({
            'body': message,
            'model': model.model,
            'res_id': record.id,
            'record_name': record.name,
            'message_type': 'comment',
            'subtype_id': self.env.ref('mail.mt_comment').id,
            'author_id': user.partner_id.id,
            'attachment_ids': [(6, 0, attachment_ids)]
        })

    def _get_service_record_access_token(self, model_id, record_id):
        model = self.env['ir.model'].browse(int(model_id))
        record = self.env[model.model].browse(record_id)
        if not record.access_token:
            return record.generate_access_token()
        return record.access_token
    
class HRServiceItems(models.Model):
    _name = 'hr.service.items'
    _description = 'HR Service Items'
    _order = 'sequence, id'
        
    sequence = fields.Integer(string='Sequence', default=10)
    hr_service_id = fields.Many2one('hr.service', string='HR Service')
    # hr_service_id = fields.Many2one('hr.service', string='HR Service', readonly=True,)
    name = fields.Text(string='Description', )
    
    field_id = fields.Many2one('ir.model.fields', string='Field', ondelete="cascade", required=True)
    field_name = fields.Char(related='field_id.name')
    field_label = fields.Char(string='Label', store=True, compute='_compute_label_from_field', readonly=False)
    field_type = fields.Selection(related='field_id.ttype')
    field_model = fields.Char(related='field_id.relation')
    field_store = fields.Boolean(related='field_id.store')
    field_readonly = fields.Boolean(related='field_id.readonly')
    field_domain = fields.Char(string='Domain Filter', help="Domain to filter records for the frontend. Use Odoo domain format.")
    search_fields_ids = fields.Many2many(
        'ir.model.fields', string='Search Fields',
        relation='service_item_search_field_rel',  # Name of the relation table
        help="Fields to be used for searching in the frontend."
    )
    label_fields_ids = fields.Many2many(
        'ir.model.fields', string='Label Fields',
        relation='service_item_label_field_rel',  # Name of the relation table
        help="Fields to be concatenated for display in the frontend."
    )
    

    # Reference fields
    ref_field_id = fields.Many2one('ir.model.fields', string='Reference Field', ondelete="cascade", help='Get value from Reference field' )
    link_field_id = fields.Many2one('ir.model.fields', string='Link Field', help="Reference field ID for many2many ")
    link_record = fields.Boolean(string='Link Record')
    is_required = fields.Boolean(string='Required', help='Required field at web form')
    
    operation_mode = fields.Selection([
        ('create', "Create"),
        ('edit', "Edit"),
        ('all', "All"),
        ], default=False, help="Technical field for operations purpose.")
    
    field_variant_line_id = fields.Many2one('hr.service.field.variant.line')

    display_option = fields.Selection([
        ('form', 'Form'),
        ('list', 'List'),
        ('both', 'Both'),
        ], string='Display View')
    
    #ref_populate_field_id = fields.Many2one('ir.model.fields',string='Filter Reference')
    ref_populate_field_id = fields.Many2one('ir.model.fields',string='Populate Field',domain="[('id', 'in', ref_populate_field_ids)]")
                
    ref_populate_field_ids = fields.Many2many('ir.model.fields',
        string='Update Fields Values',
        compute='_compute_related_model_for_populate_field',
    )

    populate_list_expr = fields.Char(string='List Expr.')
    change_field_exp = fields.Char(string='Expression')

    ref_changeable_field_ids = fields.Many2many('ir.model.fields',
        string='Changable Fields', readonly=True,
        #compute='_compute_fields_from_expression',
    )

    
    is_model_selected = fields.Boolean(compute='_compute_is_model_selected')

    #@api.depends('change_field_exp')
    def _compute_fields_from_expression(self):
        for record in self:
            pass

    @api.depends('field_model')
    def _compute_is_model_selected(self):
        for record in self:
            record.is_model_selected = bool(record.field_model)


    @api.depends('field_id')
    def _compute_related_model_for_populate_field(self):
        for record in self:
            related_fields = self.env['ir.model.fields'].search([('model', '=', record.hr_service_id.header_model_id.model), ('ttype', '=', 'many2one')])
            record.ref_populate_field_ids = related_fields         

    @api.depends('field_id')
    def _compute_label_from_field(self):
        for line in self:
            line.field_label = line.field_id.field_description
            
    @api.onchange('field_id')
    def _field_id_onchange(self):
        for line in self:
            line.is_required = False
            #line.is_create = False
            #line.is_edit = False
            line.link_record = False

    
    @api.onchange('field_model')
    def _onchange_field_model(self):
        domain = {}
        if self.field_model:
            domain['search_fields_ids'] = [('model', '=', self.field_model),('store', '=', True),('ttype', 'in', ['char','integer','text','selection'])]
            domain['label_fields_ids'] = [('model', '=', self.field_model),('store', '=', True),('ttype', 'in', ['char','integer','text','selection'])]
            # Clear the current values of the fields
            self.search_fields_ids = False
            self.label_fields_ids = False
        else:
            domain['search_fields_ids'] = []
            domain['label_fields_ids'] = []
            # Clear the current values of the fields
            self.search_fields_ids = False
            self.label_fields_ids = False
        return {'domain': domain}

                
class HRServiceItemsLine(models.Model):
    _name = 'hr.service.record.line'
    _description = 'Service Record Line'
    _order = 'sequence, id'
    
    hr_service_id = fields.Many2one('hr.service', string='HR Service', readonly=True,)
    header_model_id = fields.Many2one('ir.model', related='hr_service_id.header_model_id')
    relational_field_id = fields.Many2one('ir.model.fields', string='Line records Field', ondelete="cascade", required=True)
    
    line_model_id = fields.Many2one('ir.model', ondelete='cascade', string='Line Item Model', store=True, compute='_compute_model_from_relational_field')
    parent_relational_field_id = fields.Many2one('ir.model.fields', string='Parent Relational', ondelete="cascade", store=True, compute='_compute_model_from_relational_field')

    sequence = fields.Integer(string='Sequence', default=10)
    hr_service_record_line_items = fields.One2many('hr.service.record.line.items', 'hr_service_record_line_id', string='Record Line Items', copy=True, auto_join=True)
    allow_import = fields.Boolean(string='Allow Import', store=True, readonly=False,  help='Allow import to user on portal')
    file_attachment = fields.Binary(string="File Attachment")
    # field_variant_id = fields.Many2one('hr.service.field.variant',related='hr_service_id.field_variant_id')
    # field_variant_line_id = fields.Many2one('hr.service.field.variant.line' )


    @api.depends('relational_field_id')
    def _compute_model_from_relational_field(self):
        model_id = self.env['ir.model']
        field_id = self.env['ir.model.fields']
        for line in self:
            model_id = self.env['ir.model'].search([('model','=',line.relational_field_id.relation)],limit=1)
            field_id = self.env['ir.model.fields'].sudo().search([('model_id','=',model_id.id),('relation','=',line.header_model_id.model)],limit=1)
            line.line_model_id = model_id.id
            line.parent_relational_field_id = field_id.id
            
        
    def action_create_record_line_items(self):
        
        self.ensure_one()

        hr_service_id = self.hr_service_id

        view = self.env.ref('de_portal_hr_service.view_service_record_line_items_wizard')

        return {
            'name': _('Record Line Items'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.service.record.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context,
            ),
        }

        
    
class HRServiceItemsLine(models.Model):
    _name = 'hr.service.record.line.items'
    _description = 'Service Record Line Items'
    _order = 'id'

    hr_service_id = fields.Many2one('hr.service', string='HR Service', readonly=True,)
    hr_service_record_line_id = fields.Many2one('hr.service.record.line', string='Service Record Line', readonly=True,)
    
    sequence = fields.Integer(string='Sequence', default=10)
    field_id = fields.Many2one('ir.model.fields', string='Field', ondelete="cascade", required=True, )
    name = fields.Text(string='Description', required=False)

    field_name = fields.Char(related='field_id.name')
    field_type = fields.Selection(related='field_id.ttype')
    field_model = fields.Char(related='field_id.relation')
    field_store = fields.Boolean(related='field_id.store')
    field_readonly = fields.Boolean(related='field_id.readonly')
    field_domain = fields.Char(string='Domain Filter', help="Domain to filter records for the frontend. Use Odoo domain format.")
    search_fields_ids = fields.Many2many(
        'ir.model.fields', string='Search Fields',
        relation='service_line_item_search_field_rel',  # Name of the relation table
        domain="[('model', '=', 'product.product')]",
        help="Fields to be used for searching in the frontend."
    )
    label_fields_ids = fields.Many2many(
        'ir.model.fields', string='Label Fields',
        relation='service_line_item_label_field_rel',  # Name of the relation table
        domain="[('model', '=', 'product.product')]",
        help="Fields to be concatenated for display in the frontend."
    )

    link_field_id = fields.Many2one('ir.model.fields', string='Link Field', help="Reference model field to display value ")
    field_label = fields.Char(string='Label', required=True, store=True, compute='_compute_label_from_field', readonly=False)
    is_required = fields.Boolean(string='Required', help='Required field at web form')
    
    # Reference fields
    ref_field_id = fields.Many2one('ir.model.fields', string='Reference Field', ondelete="cascade", help='Get value from Reference field' )
    
    field_variant_id = fields.Many2one('hr.service.field.variant',related='hr_service_id.field_variant_id')
    field_variant_line_id = fields.Many2one('hr.service.field.variant.line')
    ref_populate_field_id = fields.Many2one('ir.model.fields',string='Populate Field',domain="[('id', 'in', ref_populate_field_ids)]")
                
    ref_populate_field_ids = fields.Many2many('ir.model.fields',
        string='ref_populate_field_ids',
        compute='_compute_related_model_for_populate_field',
    )
    populate_list_expr = fields.Char(string='List Expr.')
    change_field_exp = fields.Char(string='Expression')

    ref_changeable_field_ids = fields.Many2many('ir.model.fields',
        string='Changable Fields', readonly=True,
        #compute='_compute_fields_from_expression',
    )
    
    operation_mode = fields.Selection([
        ('create', "Create"),
        ('edit', "Edit"),
        ('all', "All"),
        ], default=False, help="Technical field for operations purpose.")

    is_model_selected = fields.Boolean(compute='_compute_is_model_selected')

    @api.depends('field_model')
    def _compute_is_model_selected(self):
        for record in self:
            record.is_model_selected = bool(record.field_model)

    
    @api.depends('field_id')
    def _compute_label_from_field(self):
        for line in self:
            line.field_label = line.field_id.field_description

    @api.depends('field_id')
    def _compute_related_model_for_populate_field(self):
        for record in self:
            related_fields = self.env['ir.model.fields'].search([('model', '=', record.hr_service_record_line_id.line_model_id.model), ('ttype', '=', 'many2one')])
            record.ref_populate_field_ids = related_fields 
            
    @api.onchange('field_model')
    def _onchange_field_model(self):
        domain = {}
        if self.field_model:
            domain['search_fields_ids'] = [('model', '=', self.field_model),('store', '=', True),('ttype', 'in', ['char','integer','text','selection'])]
            domain['label_fields_ids'] = [('model', '=', self.field_model),('store', '=', True),('ttype', 'in', ['char','integer','text','selection'])]
            # Clear the current values of the fields
            self.search_fields_ids = False
            self.label_fields_ids = False
        else:
            domain['search_fields_ids'] = []
            domain['label_fields_ids'] = []
            # Clear the current values of the fields
            self.search_fields_ids = False
            self.label_fields_ids = False
        return {'domain': domain}