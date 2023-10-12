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

    hunter_instance_id = fields.Many2one(
        'hunter.instance',
        string='Hunter Instance',
        default=lambda self: self._compute_default_hunter_instance(),
        domain = "[('state','=','active')]"
    )

    def _compute_default_hunter_instance(self):
        # Find an APL instance record in the current company and return its ID
        hunter_instance = self.env['hunter.instance'].search([
            ('company_id', '=', self.env.company.id),('state', '=', 'active')
        ], limit=1)  # Limit to one record (if available)

        return hunter_instance.id if hunter_instance else False

    api_type = fields.Selection([
        ('domain', 'Domain Search'), ('company', 'Company Search'),
        ('email_domain', 'Find Emails by Domain'), ('email_company', 'Find Emails by Company'),
        ('email_name', 'Find Email by Name'), ('email_verify', 'Verify Email')
    ], required=True, string="Operation Type", default='domain')

    line_ids = fields.One2many('hunter.api.call.wizard.line', 'wizard_id', string='Lines')


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

    name = fields.Char(string='Name')
    email = fields.Char(string='email')
    # Add other fields as needed
    wizard_id = fields.Many2one('hunter.api.call.wizard', string='Related Wizard')
