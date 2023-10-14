# -*- coding: utf-8 -*-

import requests
import json

from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError, ValidationError
import pprint

from urllib.parse import urlparse

class res_partner(models.Model):
    _inherit = 'res.partner'

    email_verified = fields.Char(string='Email Verified')
    
    def action_find_email(self):
        hunter_instance_id = self.company_id.hunter_instance_id or self.env.company.hunter_instance_id
        for record in self:
            if not (record.name):
                raise UserError("Please provide at least one of the following values: Company Name, Customer, or Contact Name.")

            data = {}
            company_name = ''
            # Domain Parameter
            parsed_url = urlparse(record.website)
            domain = parsed_url.hostname
            if domain and domain.startswith('www.'):
                domain = domain[4:]

            # Company Name Paramter
            if record.name:
                company_name = record.name
                    
            if record.website:
                data['domain'] = domain
            else:
                if company_name:
                    data['company'] = company_name

            # add the first name
            if company_name:
                name_parts = record.name.split()
                first_name = name_parts[0]
                last_name = name_parts[-1]
                data['first_name'] = first_name
                data['last_name'] = last_name
            
            json_data = hunter_instance_id._get_from_hunter('email-finder', data)
            email = json_data['data']['email']
            verification_status = json_data['data']['verification']['status']
            if email:
                record.write({
                    'email': email,
                    'email_verified':verification_status,
                })
            else:
                raise UserError("No email found for '%s'." % company_name)
                
    def action_find_bulk_emails(self):
        for record in self:
            #record._send_to_apollo(self.apl_instance_id)
            hunter_instance_id = record.company_id.hunter_instance_id or self.env.company.hunter_instance_id
            data = {}
            domain = ''
            # Domain Parameter
            if record.website:
                parsed_url = urlparse(record.website)
                domain = parsed_url.hostname
                if domain.startswith('www.'):
                    domain = domain[4:]
                data['domain'] = domain

            # Company Name Paramter
            if record.name:
                company_name = record.name
                data['company'] = company_name

            #raise UserError(company_name)
            
            json_data = hunter_instance_id._get_from_hunter('domain-search', data)

            #company_name = json_data['data']['organization']
            company_domain = json_data['data']['domain']

            country = json_data['data']['country']
            state = json_data['data']['state']
            city = json_data['data']['city']
            postal_code = json_data['data']['postal_code']
            street = json_data['data']['street']
    
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
                    "country": country,
                    "state": state,
                    "city": city,
                    "postal_code": postal_code,
                    "street": street,
                    "partner_id": record.id,
                })
                self.env['hunter.results'].search([('create_uid', '=', self.env.user.id)]).sudo().unlink()
                result_id = self.env['hunter.results'].create(contact_info)

        return {
            'name': _('Find Emails'),
            'res_model': 'hunter.api.call.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'res.partner',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_email_verify(self):
        for record in self:
            if not record.email:
                raise UserError("Please enter email for verification.")
            hunter_instance_id = record.company_id.hunter_instance_id or self.env.company.hunter_instance_id
            data = {
                'email': record.email,
            }
            json_data = hunter_instance_id._get_from_hunter('email-verifier', data)
            status = json_data['data']['status']
            record.write({
                'email_verified':status,
            })