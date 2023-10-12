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

    name_update = fields.Boolean(string='Name', default=True)
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
            for lead in record_ids:
                results = self.env['hunter.results'].search([])
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
            #raise UserError(len(selected_line))
            #if len(selected_line) != 1:
            #    raise UserError("You must select only one record.")
            lead_id = self.env[self.active_model].browse(self.env.context.get('active_id'))
            for line in selected_lines:
                vals = {}
                if record.email_update:
                    vals['email_from'] = line.email
                if record.name_update:
                    vals['contact_name'] = line.name
                if record.position_update:
                    vals['function'] = line.position
                if record.phone_update:
                    vals['phone'] = line.phone
                    
                lead_id.write(vals)

        
    def action_process(self):
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])

        
        #raise UserError(active_ids)
        
        record_ids = self.env[active_model].search([('id','in',active_ids)])
        data = {}
        for record in record_ids:
            #record._send_to_apollo(self.apl_instance_id)

            if self.api_type in ('domain','email_domain'):
                # Domain Parameter
                if record.website:
                    parsed_url = urlparse(record.website)
                    domain = parsed_url.hostname
                    if domain.startswith('www.'):
                        domain = domain[4:]
                    data['domain'] = domain

            if self.api_type in ('company','email_company'):
                # Company Name Paramter
                if record.partner_name:
                    company_name = record.partner_name
                elif record.partner_id:
                    if record.partner_id.parent_id:
                        company_name = record.partner_id.parent_id.name
                    else:
                        company_name = record.partner_id.name
                if company_name:
                    data['company'] = company_name

            if self.api_type in ('email_name'):
                # Contact Name
                if record.contact_name:
                    data['full_name'] = record.contact_name

            if self.api_type in ('email_verify'):
                # Email
                if record.email_from:
                    data['email'] = record.email_from
                                                
            data = record.company_id.hunter_instance_id._get_from_hunter('domain-search', data)
            emails = data['data']['emails']
            contact_info = []
            for email_data in emails:
                email = email_data['value']
                first_name = email_data['first_name']
                last_name = email_data['last_name']
                
                # Combine first name and last name or use the email if names are not available
                contact_name = f"{first_name} {last_name}" if first_name and last_name else email
                
                contact_info.append({
                    "email": email,
                    "contact_name": contact_name,
                    "wizard_id" :self.id,
                })
                result_id = self.env['hunter.api.call.wizard.line'].create(contact_info)

        # Define the action to prevent the window from closing
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hunter.api.call.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': False,
            'target': 'new',
        }

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
