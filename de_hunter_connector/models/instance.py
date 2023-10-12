# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _
from odoo.exceptions import UserError, AccessError
from odoo.tools import html_escape as escape

import requests
import json

from urllib.parse import urlparse


READONLY_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'verified', 'active'}
}

class HunterInstance(models.Model):
    _name = 'hunter.instance'
    _description = 'Apollo Instance'

    name = fields.Char(string='Name', required=True, )
    api_key = fields.Char(string='API Key', required=True, help='Secret API Key', )
    url = fields.Char(string='URL', required=True, )

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, states=READONLY_FIELD_STATES, default=lambda self: self.env.company)


    state = fields.Selection([
        ('draft', 'Draft'), 
        ('verified', 'Verified'), 
        ('active', 'Active')], 
        string='Status',default='draft', required=True
    )


    def button_draft(self):
        url = 'https://api.hunter.io/v2/domain-search?domain=stripe.com&api_key=c9280ab0813d7fee78ef90d0576ba532d09adc3f'
        url = self.url + 'domain-search?domain=dynexcel.com&api_key=' + self.api_key
        headers = {
            'X-API-KEY': self.api_key,
        }
        response = requests.request("GET", url, headers=headers)

        raise UserError(response.text)
        
        self.write({
            'state':'draft'
        })

    def button_confirm(self):
        self.write({
            'state':'active'
        })
        
    def connection_test(self):
        
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Connection to Apollo successful; explore its capabilities now.'),
                'type': 'warning',
                'sticky': False,  #True/False will display for few seconds if false
            },
        }

        url = self.url + '' #"https://api.apollo.io/v1/auth/health"
        url = 'https://api.hunter.io/v2/domain-search?domain=stripe.com&api_key=c9280ab0813d7fee78ef90d0576ba532d09adc3f'
        url = self.url + 'domain-search?domain=dynexcel.com&api_key=' + self.api_key
        headers = {
            'X-API-KEY': self.api_key,
        }
        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200: 
            self.write({
                'state': 'verified'
            })
            notification['params'].update({
                'title': _('The connection to Apollo was successful.'),
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            })
            
        else:
            # The response indicates an error
            error_message = "API connection error. Please check the response."
            raise UserError(error_message)
        return notification

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError("You cannot delete a record with a state other than 'draft'.")
        return super(ApolloInstance, self).unlink()

        
    

    # ---------------------------------------------------------
    # ---------------------- Operations for Hunter ------------
    # ---------------------------------------------------------
    
    @api.model
    def _post_apollo_data(self, api_name, api_data=None):
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
            #raise UserError(url)
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

    @api.model
    def _get_from_hunter(self, api_name, api_data=None):

        #url = self.url + 'domain-search?domain=dynexcel.com&api_key=' + self.api_key
        headers = {
            'X-API-KEY': self.api_key,
        }
        
        try:
            
            if api_data is None:
                api_data = {}

            # Add the api_key field to the data dictionary
            api_data['api_key'] = self.api_key

            # Initialize an empty string
            query_string = ""
    
            # Iterate through the dictionary items
            for key, value in api_data.items():
                if query_string:
                    query_string += "&"
                else:
                    query_string += "?"
                query_string += f"{key}={value}"

            url = self.url+api_name+query_string
            #raise UserError(url)
            

            response = requests.request("GET", url, headers=headers)
            #raise UserError(response.text)
            json_data = json.loads(response.text)
            return json_data

        except requests.exceptions.RequestException as e:
            # Handle any request exceptions
            raise e

        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            raise e

    @api.model
    def _put_apollo_data(self, api_name, api_data=None):
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

            response = requests.request("PUT", url, headers=headers, params=api_data)
            #raise UserError(response.text)
            json_data = json.loads(response.text)
            return json_data

        except requests.exceptions.RequestException as e:
            # Handle any request exceptions
            raise e

        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            raise e

