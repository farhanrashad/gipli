# -*- coding: utf-8 -*-

import requests
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from urllib.parse import urlparse

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
        person_data = {}
        company_data = {}
        account_data = {}
        for partner in partner_ids:

            # check is this contact or company
            if partner.company_type == company:
                company_partner = partner
            else:
                company_partner = partner.parent_id

            # Fist name and Second name
            split_names = partner.name.split(" ", 1)  # Split at the first space
            if len(split_names) == 2:
                first_name, last_name = split_names

            if partner.company_type == 'person':
                #raise UserError(last_name)
                person_data = {
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
            if company_partner:
                data["organization_name"] = partner.parent_id.name

                # parse website domain of parent 
                parsed_url = urlparse(partner.parent_id.website)
                domain = parsed_url.hostname
                
                company_data = {
                    "name": partner.parent_id.name,
                    "website_url": partner.parent_id.website,
                    "blog_url": partner.parent_id.blog_url,
                    "angellist_url": partner.parent_id.angellist_url,
                    "linkedin_url": partner.parent_id.linkedin_url,
                    "twitter_url": partner.parent_id.twitter_url,
                    "facebook_url": partner.parent_id.facebook_url,
                    #"primary_phone": {},
                    #"languages": [],
                    #"alexa_ranking": null,
                    "phone": partner.parent_id.phone,
                    #"linkedin_uid": "40897764",
                    "founded_year": null,
                    #"publicly_traded_symbol": null,
                    #"publicly_traded_exchange": null,
                    #"logo_url": "https://zenprospect-production.s3.amazonaws.com/uploads/pictures/63cd3e8cb31fb400018d4b61/picture",
                    #"crunchbase_url": null,
                    "primary_domain": domain,
                }
                account_date = {
                    "name": partner.parent_id.name,
                    "website_url": partner.parent_id.website,
                    "blog_url": partner.parent_id.blog_url,
                    "angellist_url": partner.parent_id.blog_url,
                    "linkedin_url": partner.parent_id.blog_url,
                    "twitter_url": partner.parent_id.blog_url,
                    "facebook_url": partner.parent_id.blog_url,
                    #"primary_phone": {
                    #    "number": "+918602017706",
                    #    "source": "Scraped",
                    #    "country_code_added_from_hq": true
                    #},
                    #"languages": [],
                    #"alexa_ranking": null,
                    "phone": "+918602017706",
                    #"linkedin_uid": "13368669",
                    "founded_year": 2007,
                    #"publicly_traded_symbol": null,
                    #"publicly_traded_exchange": null,
                    #"logo_url": "https://zenprospect-production.s3.amazonaws.com/uploads/pictures/63bfbeee7fb7aa0001605365/picture",
                    #"crunchbase_url": null,
                    "primary_domain": domain,
                    "sanitized_phone": "+918602017706",
                    "domain": domain,
                    #"team_id": "63f7d4e7c63f0300a3804ee9",
                    "organization_id": "5a9dd948a6da98d9a15ba541",
                    "account_stage_id": "63f7d4e7c63f0300a3804ef4",
                    "source": "deployment",
                    "original_source": "deployment",
                    #"creator_id": null,
                    #"owner_id": "63f7d4e8c63f0300a3804f65",
                    #"created_at": "2023-04-08T11:23:17.428Z",
                    #"phone_status": "no_status",
                    #"hubspot_id": null,
                    #"salesforce_id": null,
                    #"crm_owner_id": null,
                    #"parent_account_id": null,
                    #"account_playbook_statuses": [],
                    #"account_rule_config_statuses": [],
                    #"existence_level": "full",
                    #"label_ids": [],
                    #"typed_custom_fields": {},
                    #"modality": "account"
                }
                
            data = self.apl_instance_id._post_apollo_data('contacts', data)
            
            apl_id = data["contact"]["id"]
                        
            #raise UserError(contact_values)    
            contact_id = partner.write({
                'apl_id': apl_id,
            })

    def _send_lead_to_apollo(self, record_ids):
        pass
        