# -*- coding: utf-8 -*-

import requests
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class APLSendDataWizard(models.TransientModel):
    _name = "apl.send.data.wizard"
    _description = 'Search People Wizard'

    apl_instance_id = fields.Many2one('apl.instance')

    def action_process(self):
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])
        if active_model == 'res.partner':
            self.sudo()._send_res_partner_to_apollo(active_ids)
        elif active_model == 'crm.lead':
            self.sudo()._send_lead_to_apollo(active_ids)

    def _send_res_partner_to_apollo(self, record_ids):
        self.ensure_one()
        partner_ids = self.env['res.partner'].search([('id','in',record_ids)])
        date = {}
        for partner in partner_ids:
            split_names = partner.name.split(" ", 1)  # Split at the first space
            if len(split_names) == 2:
                first_name, last_name = split_names
            #raise UserError(last_name)
            data = {
                "first_name": first_name,
                "last_name": last_name,
                "name": partner.name,
                "title": partner.function if partner.function else '',
                "headline": partner.function,
                #"organization_name": "Dynexcel",
                "email": partner.email if partner.email else '',
                "website_url": partner.website if partner.website else '',
                "city": partner.city if partner.city else '',
                "state": partner.state_id.name if partner.state_id else '',
                "country": partner.country_id.name if partner.country_id else '',
                "present_raw_address": partner.city if partner.city else '' + ", " + partner.state_id.name if partner.state_id else '' + ", " + partner.country_id.name if partner.country_id else '',
                "phone_numbers": [
                    {
                      "raw_number": "+923001616395",
                      "sanitized_number": "+923001616395",
                      "type": "work_hq",
                      "position": 0,
                      "status": "no_status",
                      "dnc_status": '',
                      "dnc_other_info": ''
                    },
                    {
                      "raw_number": "+923001616396",
                      "sanitized_number": "+923001616396",
                      "type": "mobile",
                      "position": 1,
                      "status": "valid_number",
                      "dnc_status": '',
                      "dnc_other_info": ''
                    }
                  ],
                #"label_names",
                #"present_raw_address":
            }
            if partner.parent_id:
                data["organization_name"] = partner.parent_id.name
                company_data = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "name": partner.name,
                    "title": partner.function if partner.function else '',
                    "headline": partner.function,
                    #"organization_name": "Dynexcel",
                    "email": partner.email if partner.email else '',
                    "website_url": partner.website if partner.website else '',
                    "city": partner.city if partner.city else '',
                    "state": partner.state_id.name if partner.state_id else '',
                    "country": partner.country_id.name if partner.country_id else '',
                }
                
            data = apl_instance_id.fetch_json_data('contacts', data)
            
            apl_id = data["contact"]["id"]
            
            # Check if data is a list, and if it is, assign it to people_data
            if isinstance(data, list):
                people_data = data
            # If data is a dictionary, check if 'people' key exists and assign it to people_data
            elif isinstance(data, dict):
                contact_data = data.get('contacts', [])
        
            contact_values = {}
            for contact in contact_data:
                contact_values = {
                    'apl_id': contact.get('id'),
                }
            #raise UserError(contact_values)    
            contact_id = self.write({
                'apl_id': apl_id,
            })

    def _send_lead_to_apollo(self, record_ids):
        pass
        