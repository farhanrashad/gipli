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
    _description = 'Hunter Instance'

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
                'title': _('Connection to Hunter successful; explore its capabilities now.'),
                'type': 'warning',
                'sticky': False,  #True/False will display for few seconds if false
            },
        }

        url = self.url + '' #"https://api.hunter.io/v1/auth/health"
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
                'title': _('The connection to Hunter was successful.'),
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
        return super(HunterInstance, self).unlink()

        
    

    # ---------------------------------------------------------
    # ---------------------- Operations for Hunter ------------
    # ---------------------------------------------------------
    
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
            raise UserError(response.text)
            json_data = json.loads(response.text)
            return json_data

        except requests.exceptions.RequestException as e:
            # Handle any request exceptions
            raise e

        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            raise e
