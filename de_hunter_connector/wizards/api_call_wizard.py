# -*- coding: utf-8 -*-

import requests
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import pprint

from urllib.parse import urlparse

class HunterApiCallWizard(models.TransientModel):
    _name = "hunter.api.call.wizard"
    _description = 'Search People Wizard'

    name_update = fields.Boolean(string='Name', 
        default=lambda self: False if self._context.get('active_model') == 'res.partner' else True
    )
    email_update = fields.Boolean(string='Email',default=True)
    position_update = fields.Boolean(string='Position', default=True)
    phone_update = fields.Boolean(string='Phone', default=True)

    
    record_select = fields.Boolean('Select Record')
    record_unselect = fields.Boolean('UnSelect Record', default=True)
    
    line_ids = fields.One2many('hunter.api.call.wizard.line', 'wizard_id', string='Lines', readonly=False, store=True, compute='_compute_line_ids')

    active_model = fields.Char(string='Model', readonly=True)

    @api.onchange('record_select')
    def _onchange_record_select(self):
        for line in self.line_ids:
            if self.record_select:
                line.write({
                    'record_select': True,
                })
            else:
                line.write({
                    'record_select': False,
                })
            #line.record_select = self.record_select

    @api.onchange('record_unselect')
    def _onchange_record_unselect(self):
        for line in self.line_ids:
            line.record_select = False
            
    @api.model
    def default_get(self, fields):
        res = super(HunterApiCallWizard, self).default_get(fields)
        if 'active_model' in self._context:
            res['active_model'] = self._context.get('active_model')
        return res
        
    @api.depends('active_model')
    def _compute_line_ids(self):
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])        
        record_ids = self.env[active_model].search([('id','in',active_ids)])

        #raise UserError(record_ids)
        for wizard in self:
            lines = []
            for record in record_ids:
                if active_model == 'crm.lead':
                    results = self.env['hunter.results'].search([('lead_id','=',record.id)])
                elif active_model == 'res.partner':
                    results = self.env['hunter.results'].search([('partner_id','=',record.id)])
                    
                for result in results:
                    vals = {
                        'name': result.name,
                        'email': result.email,
                        'wizard_id': wizard.id,  # Set the wizard ID for the line record
                    }
                    line = self.env['hunter.api.call.wizard.line'].create(vals)
                    lines.append(line.id)
            wizard.line_ids = [(6, 0, lines)]
    
    
    # -------------------------------------------
    # ---------------- Actions ------------------
    # -------------------------------------------
    def action_update_email(self):
        for record in self:
            vals = {}
            selected_lines = record.line_ids.filtered(lambda r: r.record_select)
            active_model = self.env.context.get('active_model')
            #raise UserError(len(selected_line))
            #if len(selected_line) != 1:
            #    raise UserError("You must select only one record.")
            record_id = self.env[self.active_model].browse(self.env.context.get('active_id'))
            for line in selected_lines:
                vals = {}
                if active_model == 'crm.lead':
                    if record.email_update:
                        vals['email_from'] = line.email
                    if record.name_update:
                        vals['contact_name'] = line.name
                    if record.position_update:
                        vals['function'] = line.position
                    if record.phone_update:
                        vals['phone'] = line.phone
                        
                
                elif active_model == 'res.partner':
                    if record.email_update:
                        vals['email'] = line.email
                    if record.position_update:
                        vals['function'] = line.position
                    if record.phone_update:
                        vals['phone'] = line.phone
                        
                record_id.write(vals)

        
    def action_convert_contacts(self):
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])        
        
        record_ids = self.env[active_model].search([('id','in',active_ids)])

        for record in record_ids:
            vals = {}
            for line in self.line_ids.filtered(lambda x: x.record_select):
                vals = {
                    'name': line.name,
                    'phone': line.phone,
                    'email': line.email,
                    'function': line.position,
                    'company_type': 'person',
                    'type': 'contact',
                }
                if active_model == 'crm.lead':
                    if record.partner_id:
                        vals['parent_id'] = record.partner_id.id
                elif active_model == 'res.partner':
                    vals['parent_id'] = record.id
                        
                partner_id = self.env['res.partner'].create(vals)

class HunterApiCallWizardResults(models.TransientModel):
    _name = 'hunter.api.call.wizard.line'
    _description = 'Hunter API Call Wizard Results'

    name = fields.Char(string='Name', readonly=True)
    email = fields.Char(string='Email', readonly=True)
    position = fields.Char(string='Position', readonly=True)
    department = fields.Char(string='Department', readonly=True)
    phone = fields.Char(string='Phone', readonly=True)
    
    record_select = fields.Boolean('Select Record', )
    # Add other fields as needed
    wizard_id = fields.Many2one('hunter.api.call.wizard', string='Related Wizard')
