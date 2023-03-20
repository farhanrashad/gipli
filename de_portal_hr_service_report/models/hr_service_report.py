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

    

class HRServiceReport(models.Model):
    _name = 'hr.service.report'
    _description = 'Service Reports'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'id'
    _sql_constraints = [('code_unique', 'unique(code)', 'code already exists!')]
    
    
    READONLY_STATES = {
        'validate': [('readonly', True)],
        'publish': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    
    def _compute_query_tooltip(self):
        for record in self:
            record.query_tooltip = _(
                    "Use syntax for parameters: field_name= %(prameter_field_name)s "
                    " - "
                    "select e.id, e.name from hr_employee e where e.department_id= %(x_department_id)s"
                )
            

    name = fields.Char(string='Name', required=True, translate=True, states=READONLY_STATES,)
    code = fields.Char(string='Code', required=True, states=READONLY_STATES)

    model_id = fields.Many2one(
            string='Model for Parameters',
            comodel_name='ir.model',
            readonly=True,
            store=True, states=READONLY_STATES,
        )

    sql_text = fields.Text(string='SQL Query', states=READONLY_STATES,)
    query_tooltip = fields.Text(compute='_compute_query_tooltip', default=_compute_query_tooltip)

    group_id = fields.Many2one('res.groups', string='Security Group', states=READONLY_STATES,)
    
    
    state = fields.Selection([
        ('draft', 'New'),
        ('validate', 'Validate'),
        ('publish', 'Publish'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
    
    param_field_ids = fields.Many2many(
        string='Parameter Fields',
        comodel_name='ir.model.fields', states=READONLY_STATES,
    )
          

    def generate_model(self):
        if self.code:
            transient_model_name =  'x_wizard_' + self.code.lower().replace(" ", "_")
            model_check = self.env['ir.model'].search([('model', '=', transient_model_name)])
            
            #raise UserError(transient_model_name)
            
            if not model_check:
                result = self.env['ir.model'].create({
                    'name': transient_model_name,
                    'model': transient_model_name,
                    'state': 'manual',
                    'transient': True,
                })
                self.model_id = result.id
                
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
        field_model_ids = self.env['ir.model'].search([('model', '=', self.model_id.model)])
        model_ids = self.model_id
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
                
        self.write({'state': 'publish'})
        return {}
    
    def get_record_count(self, user_id):
        records = 0
        search_domain = []
        condition_domain = []
        field_ids = self.env['ir.model.fields']
        for report in self:         
            search_domain = [('id','!=',False)]
            field_ids = self.env['ir.model.fields'].sudo().search([('model_id','=',report.model_id.id)])
            for field in field_ids:
                if field.name == 'message_partner_ids':
                    search_domain += [(field.name, '=', user_id.partner_id.id)]

            search_domain = condition_domain + search_domain
            records = self.env[report.model_id.model].sudo().search_count(search_domain)
            
        return records
    
