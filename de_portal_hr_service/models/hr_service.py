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

    allow_log_note = fields.Boolean(string='Allow Log Note', store=True, compute='_compute_allow_messages', readonly=False, states=READONLY_STATES, help='Allow Log Note to user on portal')

    
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
        return {}

    
        
    
    
    @api.depends('header_model_id')
    def _compute_allow_messages(self):
        records = 0
        for service in self:
            records = self.env['ir.model.fields'].search_count([('model_id','=',service.header_model_id.id),('name','=','website_message_ids')])
            if records > 0:
                service.allow_messages = True
                service.allow_log_note = True
            else:
                service.allow_messages = False
                service.allow_log_note = False

    def get_record_count(self, user_id):
        domain = []
        domain += expression.AND([self._get_user_domain(user_id.partner_id.id), self._get_filter_domain()])
        records = self.env[self.header_model_id.model].search_count(domain)
        return records
        
    def _get_records_filter_by_domain(self,partner_id):
        domain = []
        domain += expression.AND([self._get_user_domain(partner_id), self._get_filter_domain()])
        #domain = user_domain + filter_domain
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
        

    def get_log_notes(self, record_id):
        message_ids = self.env['mail.message'].search([
            ('res_id','=',record_id.id),
            ('model','=',self.header_model_id.model),
            ('subtype_id','=',self.env.ref('mail.mt_note').id)
        ])
        return message_ids

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

    def get_changeable_field_values(self, form_elements_json, changeable_field_ids, field_name):
        # Process the form elements JSON data
        form_elements = json.loads(form_elements_json)

        # Initialize variables for service_id, model_id, and record_id
        service_id = 0
        model_id = 0
        record_id = 0
        #field_name = ''
        
        # Iterate through form elements to find the required IDs
        for element in form_elements:
            if element['name'] == 'service_id':
                service_id = element['value']
            elif element['name'] == 'model_id':
                model_id = element['value']
            elif element['name'] == 'record_id':
                record_id = element['value']

        model = self.env['ir.model'].browse(model_id)
        computed_field_values = []
        expression_parts = ''
        changeable_field_names = ''

        service_items = self.env['hr.service.items'].search([('field_id.id','in',changeable_field_ids)])
        
        for item in service_items:
            if item.change_field_exp:
                expression_parts = item.change_field_exp.split('.')
                if len(expression_parts) >= 2:
                    f1 = expression_parts[0]
                    f2 = expression_parts[1]
                    computed_field_values.append({
                        'field1': f1, 
                        'field2': f2,
                    })

        
            #if len(expression_parts) >= 2:
            #    field_name = expression_parts[1]  # Get the field name after the '.'
                #field_model = self.env[expression_parts[0]]  # Get the model based on the first part of the expression
    
                # Search for the field in form_elements
            #    field_value = 0
            #    for element in form_elements:
            #        if element['name'] == field_name:
            #            field_value = element['value']
            #            break
    
            #    if field_value:
            #        field_record = field_model.browse(int(field_value))
            #        attribute_name = expression_parts[1]
    
            #        computed_field_value = getattr(field_record, attribute_name)
    
            #        computed_field_values.append({'name': cf.name, 'value': computed_field_value})
                    
        """
                    find before . in cf.change_field_exp expression in hr.service.items model if found then there is a field field_mode get this model and then find this field value in form_elements 
                    field_record = self.env[field_model].browse(find field value in form_elements of before . expression in change_field_exp
                    now get after . from the expression and get value field_record[after . value]
                    repeat this value if multiple values found in expression
                    e.g product_id.id + product_uom.id
                    last add the value in the list as like cf.name and the value get
        """

        # Example logic to retrieve changable field values based on provided parameters
        # Replace this with your actual logic to fetch and return the values
        changeable_field_values = {
            'service_id': service_id,
            'model_id': model_id,
            'record_id': record_id,
            'field_name': field_name,
            'changeable_field_ids': changeable_field_ids,
            'expression_parts': computed_field_values,
        }

        return changeable_field_values
    
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