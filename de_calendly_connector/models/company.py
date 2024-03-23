# -*- coding: utf-8 -*-

import requests
from odoo import models, fields
from odoo.exceptions import UserError

CALENDLY_BASE_URL = 'https://api.calendly.com'

class ResCompany(models.Model):
    _inherit = 'res.company'

    calendly_client_id = fields.Char(string='Client ID')
    calendly_client_secret = fields.Char(string='Client secret')
    calendly_access_token = fields.Char(string='Access Token')
    calendly_refresh_token = fields.Char(string='Refresh Token')
    calendly_generated_access_token = fields.Boolean(string='Access Token Generated')

    def _get_header(self):
        access_token = self.calendly_access_token
        if access_token:
            return {
                'Authorization': f'Bearer {access_token}', 
                'Accept': 'application/json'
            }
        else:
            raise UserError('Access token is not available.')
        
    def _handle_response(self, response):
        if response.status_code == 401:
            # Handle token refresh here if needed
            raise UserError('Unauthorized. Token refresh logic goes here.')
        elif not response.ok:
            raise UserError(f'Error: {response.status_code} - {response.text}')
        else:
            return response.json()

    def get_scheduled_events(self, organization=None, user=None):
        url = f'{CALENDLY_BASE_URL}/scheduled_events'
        params = {}
        if organization:
            params['organization'] = organization
        if user:
            params['user'] = user

        headers = self._get_header()
        response = requests.get(url, params=params, headers=headers)
        return self._handle_response(response)

    def get_current_user(self):
        url = f'{CALENDLY_BASE_URL}/users/me'
        params = {}
        headers = self._get_header()
        response = requests.get(url, params=params, headers=headers)
        return self._handle_response(response)
        