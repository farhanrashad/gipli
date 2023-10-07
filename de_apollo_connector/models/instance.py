# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _
from odoo.exceptions import UserError, AccessError
from odoo.tools import html_escape as escape

import requests
import json

READONLY_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'verified', 'active'}
}

class ApolloInstance(models.Model):
    _name = 'apl.instance'
    _description = 'Apollo Instance'

    name = fields.Char(string='Name', required=True)
    api_key = fields.Char(string='API Key', required=True, help='Secret API Key')
    url = fields.Char(string='URL', required=True)

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, states=READONLY_FIELD_STATES, default=lambda self: self.env.company)


    state = fields.Selection([
        ('draft', 'Draft'), 
        ('verified', 'Verified'), 
        ('active', 'Active')], 
        string='Status',default='draft', required=True
    )

    contact_syn = fields.Boolean(
        string='Contact Sync',
        help="Synchronize contact with Apollo."
    )

    lead_syn = fields.Boolean(
        string='Lead Sync',
        help="Synchronize Lead with Apollo."
    )


    def button_draft(self):

        data = {
            #"api_key": self.api_key,
            "q_organization_domains": "apollo.io\ngoogle.com",
            "page" : 1,
            "person_titles" : ["sales manager", "engineer manager"]
        }
        
        raise UserError(self.fetch_json_data('mixed_people/search', data))

        url = "https://api.apollo.io/v1/typed_custom_fields"

        querystring = {
            "api_key": self.api_key
        }

        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, params=querystring)

        raise UserError(response.text)



        url = self.url + 'mixed_people/search'
        data = {
            "api_key": self.api_key,
            "q_organization_domains": "apollo.io\ngoogle.com",
            "page" : 1,
            "person_titles" : ["sales manager", "engineer manager"]
        }
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, json=data)

        #raise UserError(response.text)
        
        data = json.loads(response.text)
        people_data = data.get('people', [])

        
        for person_data in people_data:
            raise UserError(person_data.get('email'))
        #raise UserError(people_data)
        #raise UserError(response.text)

        self.write({
            'state':'draft'
        })
    def connection_test(self):
        url = self.url + 'auth/health' #"https://api.apollo.io/v1/auth/health"
        querystring = {
            "api_key": self.api_key
        }
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        if response.status_code == 200: 
            self.write({
                'state': 'verified'
            })
            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('The connection to Apollo was successful.'),
                    'type': 'success',
                    'sticky': False,  #True/False will display for few seconds if false
                },
            }
            
        else:
            # The response indicates an error
            error_message = "API connection error. Please check the response."
            raise UserError(error_message)
        return notification

    def button_import_contacts(self):
        pass

    def button_import_leads(self):
        pass

    def button_confirm(self):
        pass


    
    @api.model
    def fetch_json_data(self, api_name, api_data=None):
        """
        Fetch JSON data from a given URL with optional data payload.
        :param url: The URL to send the request to.
        :param data: Optional data to send with the request.
        :return: JSON data received in the response.
        """
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json'
        }
        try:
            url = self.url + api_name

            # Initialize data as an empty dictionary if it's None
            if api_data is None:
                api_data = {}

            # Add the api_key field to the data dictionary
            api_data['api_key'] = self.api_key

            #raise UserError(api_data)
            
            response = requests.request("POST", url, headers=headers, json=api_data)   
            #raise UserError(response.text)
            json_data = json.loads(response.text)
            return json_data

        except requests.exceptions.RequestException as e:
            # Handle any request exceptions
            raise e

        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            raise e

