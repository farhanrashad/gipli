# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import requests
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import pprint

from urllib.parse import urlparse
class ResPartner(models.Model):
    _inherit = 'res.partner'

    apl_id = fields.Char(
        string='Apollo ID',
        help="The Apollo ID is used for tracking purposes."
    )
    apl_date_sync = fields.Date('Synronization Date', help="he date of the most recent synchronization of contacts with Apollo.")

    update_required_for_apollo = fields.Boolean('Update Required for Apollo', help="Set to 'True' when this record requires an update in Apollo.")

    linkedin_url = fields.Char('LinkedIn')
    twitter_url = fields.Char('Twitter')
    github_url = fields.Char('Github')
    facebook_url = fields.Char('Facebook')
    blog_url = fields.Char('Blog')
    angellist_url = fields.Char('Angel List')
    founded_year = fields.Integer('Founded Year', default=2001)


    def action_send_to_apollo_data(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        return {
            'name': _('Apollo'),
            'res_model': 'apl.send.data.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'res.partner',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def _cron_send_to_apollo(self):
        assign_cron = self.env["ir.config_parameter"].sudo().get_param("apl.leads.auto")
        record_ids = self.env['res.partner'].search([('update_required_for_apollo','=',True)])
        #apl_instance = self.env['apl.instance'].search([
        #    ('company_id', '=', self.env.company.id),
        #], limit=1)  # Limit to one record (if available)
        if assign_cron:
            for record in record_ids:
                record._send_to_apollo(record.company_id.apl_instance_id)
        
    def _send_to_apollo(self, apl_instance_id):
        self.ensure_one()
        
        person_data = {}
        account_data = {}

        data_acc = data_per = []

        person_apl_id = account_apl_id = ''
        
        for partner in self:

            # check is this contact or company
            if partner.company_type == 'company':
                company_partner = partner
            elif partner.parent_id.company_type == 'company':
                company_partner = partner.parent_id
            else:
                company_partner = partner.parent_id

            if company_partner:
                # parse website domain of parent 
                parsed_url = urlparse(partner.parent_id.website)
                domain = parsed_url.hostname

                # Account Date
                account_data = {
                    "name": company_partner.name,
                    "website_url": company_partner.website,
                    "blog_url": company_partner.blog_url,
                    "angellist_url": company_partner.blog_url,
                    "linkedin_url": company_partner.blog_url,
                    "twitter_url": company_partner.blog_url,
                    "facebook_url": company_partner.blog_url,
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
                    #"organization_id": "5a9dd948a6da98d9a15ba541",
                    #"organization_raw_address": "49 villiers street, london, greater london, united kingdom",
                    #"organization_city": "London",
                    #"organization_street_address": "49 Villiers Street",
                    #"organization_state": "England",
                    #"organization_country": "United Kingdom",
                    #"organization_postal_code": "WC2N 6NE",
                    #"account_stage_id": "63f7d4e7c63f0300a3804ef4",
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

                if not company_partner.apl_id:
                    data_acc = apl_instance_id._post_apollo_data('accounts', account_data)
                    account_apl_id = data_acc["account"]["id"]        
                    #raise UserError(contact_values)    
                    contact_id = company_partner.write({
                        'apl_id': account_apl_id,
                    })
                else:
                    api_str = 'accounts' + '/' + company_partner.apl_id
                    data_acc = apl_instance_id._put_apollo_data(api_str, account_data)

            # Create Contact in Apollo
            if partner.company_type == 'person':
                # Fist name and Second name
                split_names = partner.name.split(" ", 1)  # Split at the first space
                if len(split_names) == 2:
                    first_name, last_name = split_names

                
                label_names = [str(label_id.name) for label_id in partner.category_id]
                
                #raise UserError(label_names)
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
                    "label_names": label_names,
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
                }
                if company_partner:
                    person_data['account'] = account_data
                    #person_data['organization_name'] = company_partner.name,
                    #person_data['account_id'] = account_apl_id or company_partner.apl_id,

                # Create a formatted string with the dictionary content
                formatted_content = pprint.pformat(person_data)

                # Raise a UserError with the formatted content
                #raise UserError(f"Person Data:\n{formatted_content}")

                if not partner.apl_id:
                    data_per = apl_instance_id._post_apollo_data('contacts', person_data)
                    #raise UserError(data_per["contact"]["name"] )
                    if 'contact' in data_per:
                        person_apl_id = data_per['contact']['id']
                    #person_apl_id = data_per["contact"]["id"]        
                    #raise UserError(contact_values)    
                    contact_id = partner.write({
                        'apl_id': person_apl_id,
                    })
                    api_str = 'contacts' + '/' + partner.apl_id
                    person_data = {
                        "account_id": company_partner.apl_id,
                    }
                    data_per = apl_instance_id._put_apollo_data(api_str, person_data)
                else:
                    api_str = 'contacts' + '/' + partner.apl_id
                    data_per = apl_instance_id._put_apollo_data(api_str, person_data)
                    


