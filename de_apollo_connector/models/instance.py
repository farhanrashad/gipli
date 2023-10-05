# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _
from odoo.exceptions import UserError, AccessError
from odoo.tools import html_escape as escape

import requests
import json

class ApolloInstance(models.Model):
    _name = 'apollo.instance'
    _description = 'Apollo Instance'

    name = fields.Char(string='Name', required=True)
    api_key = fields.Char(string='API Key', required=True, help='Secret API Key')
    url = fields.Char(string='URL', required=True)

    state = fields.Selection([
        ('draft', 'Draft'), 
        ('verified', 'Verified'), 
        ('active', 'Active')], 
        string='Status',default='draft', required=True
    )

    def button_draft(self):
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

        


