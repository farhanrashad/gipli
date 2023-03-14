# -*- coding: utf-8 -*-

import base64
import ast
import json

from odoo import api, fields, models, tools, _
from random import randint
from odoo.exceptions import UserError
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _
from odoo.tools import safe_eval
from odoo.exceptions import ValidationError

    

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
    # filter_field_id = fields.Many2one('ir.model.fields', string='Filter By ',required=True, ondelete="cascade", states=READONLY_STATES,)
    filter_field_id = fields.Many2one('ir.model.fields', string='Filter By ',required=True, ondelete="cascade")
    
    is_create = fields.Boolean(string='Create', help='Allow record creation', states=READONLY_STATES,)
    is_edit = fields.Boolean(string='Edit', help='Allow record edition', states=READONLY_STATES,)
    allow_messages = fields.Boolean(string='Allow Messages', store=True, compute='_compute_allow_messages', readonly=False, states=READONLY_STATES, help='Allow messages to user on portal')
    
    @api.onchange('allow_messages')
    def _onchange_allow_messages(self):
        partner_id = self.env.user.partner_id
        if self.allow_messages and partner_id and self.id and self.id.origin:
            self.message_subscribe([partner_id.id])
        elif not self.allow_messages and partner_id:
            self.message_unsubscribe([partner_id.id])    


    group_id = fields.Many2one('res.groups', string='Group')
    
    hr_service_items = fields.One2many('hr.service.items', 'hr_service_id', string='Service Items', copy=True, auto_join=True, states=READONLY_STATES,)
    
    #hr_service_items_line = fields.One2many('hr.service.items.line', 'hr_service_id', string='Item Lines', copy=True, auto_join=True, states=READONLY_STATES,)

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
        self.write({'state': 'validate'})
        return {}
    
    def button_publish(self):
        field_model_ids = self.env['ir.model']
        #model_ids = self.env['ir.model']
        model_ids = self.header_model_id
        
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
        for model in field_model_ids:
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
    
    def get_record_count(self, user_id):
        records = 0
        #domain = []
        search_domain = []
        condition_domain = []
        field_ids = self.env['ir.model.fields']
        for service in self:
            #try:
            if service.filter_domain:
                search_domain = safe_eval.safe_eval(service.filter_domain)
            else:
                search_domain = [('id','!=',False)]
            #raise ValidationError(_(domain))

            field_ids = self.env['ir.model.fields'].sudo().search([('model_id','=',service.header_model_id.id)])
            for field in field_ids:#.filtered(lambda f: f.relation == 'res.partner' or f.relation == 'hr.employee'):
                if field.name == 'message_partner_ids':
                    search_domain += [(field.name, '=', user_id.partner_id.id)]
                    #condition_domain += [('&')]
                #elif 'employee' in field.name and field.relation == 'hr.employee':
                #    search_domain += [(field.name, '=', user_id.employee_id.id)]
                #    condition_domain += [('|')]
                #if field.relation == 'res.users' and field.ttype == 'many2one':
                #    search_domain += [(field.name, '=', user_id.id)]
                #    condition_domain += [('|')]
                #if field.relation == 'res.partner' and field.ttype == 'many2one':
                #    search_domain += [(field.name, '=', user_id.partner_id.id)]
                #    condition_domain += [('|')]
            #except:
            #    domain = [('id', '=', 0)]
            #domain = search_domain + domain
            
            search_domain = condition_domain + search_domain
            records = self.env[service.header_model_id.model].search_count(search_domain)
            
            #records = self.env['hr.expense.sheet'].search_count([('message_partner_ids', 'child_of', [user_id.partner_id.id])])
        return records
    
    @api.depends('header_model_id')
    def _compute_allow_messages(self):
        records = 0
        for service in self:
            records = self.env['ir.model.fields'].search_count([('model_id','=',service.header_model_id.id),('name','=','website_message_ids')])
            if records > 0:
                service.allow_messages = True
            else:
                service.allow_messages = False
    
class HRServiceItems(models.Model):
    _name = 'hr.service.items'
    _description = 'HR Service Items'
    _order = 'sequence, id'
        
    sequence = fields.Integer(string='Sequence', default=10)
    hr_service_id = fields.Many2one('hr.service', string='HR Service')
    # hr_service_id = fields.Many2one('hr.service', string='HR Service', readonly=True,)
    name = fields.Text(string='Description', )
    
    field_id = fields.Many2one('ir.model.fields', string='Field', ondelete="cascade")
    field_name = fields.Char(related='field_id.name')
    field_label = fields.Char(string='Label', store=True, compute='_compute_label_from_field', readonly=False)
    

    field_type = fields.Selection(related='field_id.ttype')
    field_model = fields.Char(related='field_id.relation')
    field_store = fields.Boolean(related='field_id.store')
    field_readonly = fields.Boolean(related='field_id.readonly')
    field_domain = fields.Char(string='Domain', help="If present, this condition must be satisfied before executing the action rule.")
    ref_field_id = fields.Many2one('ir.model.fields', string='Reference Field', ondelete="cascade", help='Get value from Reference field' )
    link_field_id = fields.Many2one('ir.model.fields', string='Link Field', help="Reference field ID for many2many ")
    
    is_required = fields.Boolean(string='Required', help='Required field at web form')
    #is_create = fields.Boolean(string='Create', help='To be avaiable field on creation form')
    #is_edit = fields.Boolean(string='Edit', help='To be avaiable field on edit form')
    
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note"),
        ('line_separator', "Separator")], default=False, help="Technical field for UX purpose.")
    
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
    
    ref_populate_field_id = fields.Many2one('ir.model.fields',string='Populate Field')



    ref_populate_field_id = fields.Many2one('ir.model.fields',string='Populate Field',domain="[('id', 'in', ref_populate_field_ids)]")
                
    ref_populate_field_ids = fields.Many2many('ir.model.fields',
        string='ref_populate_field_ids',
        compute='_compute_related_model_ids',
    )

    @api.depends()
    def _compute_related_model_ids(self):
        for record in self:
            field_ids = record.env[record._name].search([]).filtered(lambda x:x.field_type == 'many2one').field_id
            record.ref_populate_field_ids = field_ids

    
   
    link_record = fields.Boolean(string='Link Record')
    
    # auto_populate = fields.Selection([
    #     ('user', 'From User'),
    #     ('employee', 'From Users Employee'),
    #     ('partner', 'From Users Partner'),
    #     ], string='Auto Populate', )

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


    # def _get_varient_line_domain(self):
    #     variant_line_records = self.env['hr.service.field.variant.line'].search([('field_variant_id','=',self.hr_service_id.field_variant_id.id)])
    #     domain = [('id', 'in', variant_line_records.ids)]
    #     return domain

    hr_service_id = fields.Many2one('hr.service', string='HR Service', readonly=True,)
    hr_service_record_line_id = fields.Many2one('hr.service.record.line', string='Service Record Line', readonly=True,)
    
    sequence = fields.Integer(string='Sequence', default=10)
    field_id = fields.Many2one('ir.model.fields', string='Field', ondelete="cascade", required=True, )
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    name = fields.Text(string='Description', required=False)

    field_name = fields.Char(related='field_id.name')
    field_type = fields.Selection(related='field_id.ttype')
    field_model = fields.Char(related='field_id.relation')
    field_store = fields.Boolean(related='field_id.store')
    field_readonly = fields.Boolean(related='field_id.readonly')
    field_domain = fields.Char(string='Domain', help="If present, this condition must be satisfied before executing the action rule.")    
    ref_field_id = fields.Many2one('ir.model.fields', string='Reference Field', ondelete="cascade", help='Get value from Reference field' )
    # code_type = fields.Selection(string='Code Type',selection=[('selection', 'Selection'),('field_referance', 'Field Referance')])
    
    field_variant_id = fields.Many2one('hr.service.field.variant',related='hr_service_id.field_variant_id')
    field_variant_line_id = fields.Many2one('hr.service.field.variant.line')
    ref_populate_field_id = fields.Many2one('ir.model.fields',string='Populate Field',domain="[('id', 'in', ref_populate_field_ids)]")
                
    ref_populate_field_ids = fields.Many2many('ir.model.fields',
        string='ref_populate_field_ids',
        compute='_compute_related_model_ids',
    )

    @api.depends()
    def _compute_related_model_ids(self):
        for record in self:
            field_ids = record.env[record._name].search([]).filtered(lambda x:x.field_type == 'many2one').field_id
            record.ref_populate_field_ids = field_ids

    
    link_field_id = fields.Many2one('ir.model.fields', string='Link Field', help="Reference model field to display value ")
    field_label = fields.Char(string='Label', required=True, store=True, compute='_compute_label_from_field', readonly=False)
    is_required = fields.Boolean(string='Required', help='Required field at web form')
    #is_create = fields.Boolean(string='Create', help='To be avaiable field on creation form')
    #is_edit = fields.Boolean(string='Edit', help='To be avaiable field on edit form')

    operation_mode = fields.Selection([
        ('create', "Create"),
        ('edit', "Edit"),
        ('all', "All"),
        ], default=False, help="Technical field for operations purpose.")
    
    @api.depends('field_id')
    def _compute_label_from_field(self):
        for line in self:
            line.field_label = line.field_id.field_description
            
    
    
    
class HRServiceItemsLine(models.Model):
    _name = 'hr.service.items.line'
    _description = 'Service Items Line'
    _order = 'sequence, id'

    
    hr_service_id = fields.Many2one('hr.service', string='HR Service', readonly=True,)
    sequence = fields.Integer(string='Sequence', default=10)
    field_id = fields.Many2one('ir.model.fields', string='Field', ondelete="cascade", required=True, domain="[('model','=','account.custom.entry.line')]")
    field_name = fields.Char(related='field_id.name')
    field_type = fields.Selection(related='field_id.ttype')
    field_model = fields.Char(related='field_id.relation')
    field_store = fields.Boolean(related='field_id.store')
    field_readonly = fields.Boolean(related='field_id.readonly')
    field_domain = fields.Char(string='Domain', help="If present, this condition must be satisfied before executing the action rule.")
    val_expr = fields.Char(string='Expression', help="If present, this field value must be copied from expression.")

    
    link_field_id = fields.Many2one('ir.model.fields', string='Link Field', help="Reference field ID for many2many ")
    field_label = fields.Char(string='Label', required=True, store=True, compute='_compute_label_from_field', readonly=False)
    is_required = fields.Boolean(string='Required', help='Required field at web form')
    #is_create = fields.Boolean(string='Create', help='To be avaiable field on creation form')
    #is_edit = fields.Boolean(string='Edit', help='To be avaiable field on edit form')

    operation_mode = fields.Selection([
        ('create', "Create"),
        ('edit', "Edit"),
        ('all', "All"),
        ], default=False, help="Technical field for operations purpose.")
    
    # auto_populate = fields.Selection([
    #     ('user', 'From User'),
    #     ('employee', 'From Users Employee'),
    #     ('partner', 'From Users Partner'),
    #     ], string='Auto Populate', )
    
    @api.depends('field_id')
    def _compute_label_from_field(self):
        for line in self:
            line.field_label = line.field_id.field_description

