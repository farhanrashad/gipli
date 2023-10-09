# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    apl_id = fields.Char(
        string='Apollo ID',
        help="The Apollo ID is used for tracking purposes."
    )
    apl_date_sync = fields.Date('Synronization Date', help="he date of the most recent synchronization of contacts with Apollo.")

    update_required_for_apollo = fields.Boolean('Update Required for Apollo', help="Set to 'True' when this record requires an update in Apollo.")


    def action_send_to_apollo(self):
        self.ensure_one()
        apl_instance_id = self.env['apl.instance'].browse(1)
        data = {
            "api_key": 'GbYvCle7WbRW0lFKYXlArw',
            "first_name": self.name,
            "last_name": self.name,
            "title": self.function,
            "headline": self.function,
            "organization_name": "Dynexcel",
            "email": self.email,
            "website_url": self.website,
            "city": self.city,
            "state": self.state_id.name,
            "country": self.country_id.name,
            "present_raw_address": self.city + ", " + self.state_id.name + ", " + self.country_id.name,
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
        #raise UserError(data)

