# -*- coding: utf-8 -*-

import requests
from odoo import models, fields
from odoo.exceptions import UserError
from datetime import datetime, timedelta

CALENDLY_BASE_URL = 'https://api.calendly.com'

class ResCompany(models.Model):
    _inherit = 'res.company'

    calendly_client_id = fields.Char(string='Client ID')
    calendly_client_secret = fields.Char(string='Client secret')
    calendly_access_token = fields.Char(string='Access Token')
    calendly_refresh_token = fields.Char(string='Refresh Token')
    calendly_generated_access_token = fields.Boolean(string='Access Token Generated')
    calendly_token_validity = fields.Datetime('Token Validity', copy=False)
    
    def _get_header(self):
        access_token = self.calendly_access_token
        token_validity = self.calendly_token_validity
        if access_token and token_validity and datetime.now() < token_validity:
            # Access token is valid, return the header with access token
            return {
                'Authorization': f'Bearer {access_token}', 
                'Accept': 'application/json'
            }
        elif self.calendly_refresh_token:
            # Access token has expired or is invalid, use refresh token to get a new access token
            #new_access_token, new_token_validity = self._refresh_access_token(self.calendly_refresh_token)
            return {
                'Authorization': f'Bearer {new_access_token}', 
                'Accept': 'application/json'
            }
        else:
            raise UserError('Access token or refresh token is not available.')

    def _refresh_access_token(self, refresh_token):
        url = f'{CALENDLY_BASE_URL}/oauth/token'
        data = {
            'client_id': self.calendly_client_id,
            'client_secret': self.calendly_client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        response_json = response.json()

        new_access_token = response_json.get('access_token')
        expires_in = response_json.get('expires_in')

        if new_access_token and expires_in:
            # Calculate new token validity based on the expiration time
            new_token_validity = datetime.now() + timedelta(seconds=expires_in)

            # Update the company record with the new access token and token validity
            self.write({
                'calendly_access_token': new_access_token,
                'calendly_token_validity': new_token_validity,
            })
            return new_access_token, new_token_validity
        else:
            raise UserError('Failed to refresh access token.')

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

    def get_event_types(self, organization=None, user=None):
        url = f'{CALENDLY_BASE_URL}/event_types'
        params = {}
        if organization:
            params['organization'] = organization
        if user:
            params['user'] = user
        headers = self._get_header()
        response = requests.get(url, params=params, headers=headers)
        return self._handle_response(response)
        