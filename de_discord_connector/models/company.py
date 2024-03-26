# -*- coding: utf-8 -*-

import requests
from odoo import models, fields
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import json
import base64
from urllib.parse import urlencode

import http.client
import urllib.parse

DISCORD_BASE_URL = 'https://discord.com/api/v10'

class ResCompany(models.Model):
    _inherit = 'res.company'

    is_discord = fields.Boolean('Discord')
    discord_client_id = fields.Char(string='Client ID')
    discord_client_secret = fields.Char(string='Client secret')
    discord_webhook_signing_key = fields.Char(string='Webhook signing key')

    discord_authorization_code = fields.Char(string='Authorization Code')
    
    discord_access_token = fields.Char(string='Access Token')
    discord_refresh_token = fields.Char(string='Refresh Token')
    discord_token_validity = fields.Datetime('Token Validity', copy=False)
    discord_generated_access_token = fields.Boolean(string='Access Token Generated')

    def _refresh_discord_access_token(self):
        companies = self.env['res.company'].search([('active', '=', True), ('discord_refresh_token', '!=', False)])
        API_ENDPOINT = 'https://discord.com/api/v10/oauth2/token'

        for company in companies:
            client_id = company.discord_client_id
            client_secret = company.discord_client_secret
            refresh_token = company.discord_refresh_token

            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            auth = (client_id, client_secret)
            
            try:
                encoded_data = urllib.parse.urlencode(data)
                #raise UserError(encoded_data)
                response = requests.post(API_ENDPOINT, data=encoded_data, headers=headers, auth=auth)
                response.raise_for_status()
                token_data = response.json()

                company.write({
                    'discord_access_token': token_data.get('access_token'),
                    #'discord_token_type': token_data.get('token_type'),
                    #'discord_token_expires_in': token_data.get('expires_in'),
                    'discord_refresh_token': token_data.get('refresh_token'),
                    #'discord_token_scope': token_data.get('scope'),
                })
                # Process the new access token data here
            except requests.exceptions.HTTPError as err:
                # Handle HTTP errors
                raise UserError(f"Response text: {response.text}")
            except Exception as e:
                # Handle other exceptions
                raise UserError(f"Error: {e}")
        
            #company_id.write({
            #    'discord_access_token': data.get('access_token'),
            #    'discord_token_validity': fields.Datetime.now() + timedelta(seconds=data.get('expires_in')),
            #})