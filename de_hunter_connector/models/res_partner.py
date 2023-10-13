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
            # Domain Parameter
            if record.website:
                parsed_url = urlparse(record.website)
                domain = parsed_url.hostname
                if domain.startswith('www.'):
                    domain = domain[4:]
                data['domain'] = domain

            # Company Name Paramter
            if record.parent_id:
                company_name = record.parent_id.name
            else:
                company_name = record.name
            #if company_name:
                #data['company'] = company_name

            
            data = hunter_instance_id._get_from_hunter('domain-search', data)

            # Find again with company name
            if not data:
                data = {
                    'company': company_name
                }
                data = hunter_instance_id._get_from_hunter('domain-search', data)
                
            emails = data['data']['emails']
            contact_info = []
            #raise UserError(emails)
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
                    "partner_id" :self.id,
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
        pass