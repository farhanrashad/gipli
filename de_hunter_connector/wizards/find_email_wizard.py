# -*- coding: utf-8 -*-

import requests
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import pprint

from urllib.parse import urlparse

class HunterFindEmailWizard(models.TransientModel):
    _name = "hunter.find.email.wizard"
    _description = 'Find Email Wizard'

    api_type = fields.Selection([
        ('domain', 'Domain Search'), ('company', 'Company Search'),
        ('email_domain', 'Find Emails by Domain'), ('email_company', 'Find Emails by Company'),
        ('email_name', 'Find Email by Name'), ('email_verify', 'Verify Email')
    ], required=True, string="Operation Type", default='domain')

    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)

    domain = fields.Char(string='Domain')
    company_name = fields.Char(string='Company Name')
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    full_name = fields.Char(string='Full Name')
    email = fields.Char(string='Email')
    

    def action_find_emails(self):
        data = {}
        api_name = ''

        hunter_instance_id = self.company_id.hunter_instance_id or self.env.company.hunter_instance_id
        
        if self.domain:
            parsed_url = urlparse(self.domain)
            domain = parsed_url.hostname
            #if domain.startswith('www.'):
            #s    domain = domain[4:]    
            data['domain'] = self.domain
            
        if self.company_name:
            data['company'] = self.company_name
        
        if self.first_name:
            data['first_name'] = self.first_name
        if self.last_name:
            data['last_name'] = self.last_name
        if self.full_name:
            data['full_name'] = self.full_name

        if self.email:
            data['email'] = self.email

        if self.api_type in ('domain','company'):
            api_name = 'domain-search'

        json_data = hunter_instance_id._get_from_hunter('domain-search', data)
        
        company_name = json_data['data']['organization']
        company_domain = json_data['data']['domain']

        # other fields combined in description
        desc = f"Industry: {json_data['data']['industry']}\n"
        desc += f"Twitter: {json_data['data']['twitter']}\n"
        desc += f"Facebook: {json_data['data']['facebook']}\n"
        desc += f"Linkedin: {json_data['data']['linkedin']}\n"
        desc += f"Instagram: {json_data['data']['instagram']}\n"
        desc += f"Youtube: {json_data['data']['youtube']}\n"
        desc += f"Technologies: {', '.join(json_data['data']['technologies'])}"
        
        emails = json_data['data']['emails']
        contact_info = []
        for email_data in emails:
            email = email_data['value']
            first_name = email_data['first_name']
            last_name = email_data['last_name']
            position = email_data['position']
            department = email_data['department']
            phone_number = email_data['phone_number']
                
            # Combine first name and last name or use the email if names are not available
            contact_name = f"{first_name} {last_name}" if first_name and last_name else email
                
            contact_info.append({
                "email": email,
                "name": contact_name,
                "position": position,
                "department": department,
                "phone": phone_number,
                "company_name": company_name,
                "website": company_domain,
                "description": desc,
            })
            self.env['hunter.results'].search([('create_uid', '=', self.env.user.id)]).sudo().unlink()
            result_id = self.env['hunter.results'].create(contact_info)
        
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'name': _('Email Results'),
            'res_model': 'hunter.results',
            'domain': [('create_uid', '=', self.env.user.id)],
            'context': {'create': False, 'edit': False},  # Add the context here
        }
        return action