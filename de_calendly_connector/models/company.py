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
            new_access_token, new_token_validity = self._refresh_access_token(self.calendly_refresh_token)
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

    

    def get_current_user(self):
        url = f'{CALENDLY_BASE_URL}/users/me'
        params = {}
        headers = self._get_header()
        response = requests.get(url, params=params, headers=headers)
        return self._handle_response(response)

    def _get_calendly_users(self, user=None):
        url = f'{CALENDLY_BASE_URL}/user'
        params = {}
        if user:
            params['user'] = user
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

    def _get_organization_memberships(self, organization=None, user=None):
        url = f'{CALENDLY_BASE_URL}/https://api.calendly.com/organization_memberships'
        params = {}
        if organization:
            params['organization'] = organization
        if user:
            params['user'] = user
        headers = self._get_header()
        response = requests.get(url, params=params, headers=headers)
        return self._handle_response(response)

    # Events
    def _get_calendly_scheduled_events(self, organization=None, user=None):
        url = f'{CALENDLY_BASE_URL}/scheduled_events'
        params = {}
        if organization:
            params['organization'] = organization
        if user:
            params['user'] = user

        headers = self._get_header()
        response = requests.get(url, params=params, headers=headers)
        return self._handle_response(response)

    def _update_calendly_events(self, collection_data):
        calendar_event_obj = self.env['calendar.event']
        for item in collection_data:
            event_data = self._prepare_event_values(item)
            if event_data:
                existing_event = calendar_event_obj.search([('calendly_uri', '=', event_data['calendly_uri'])])
                if existing_event:
                    existing_event.write(event_data)
                else:
                    calendar_event_obj.create(event_data)
    
    def _prepare_event_values(self, event_item):
        name = event_item.get('name')
        uri = event_item.get('uri')
        start_time_str = event_item.get('start_time')
        end_time_str = event_item.get('end_time')
        location = event_item.get('location', {}).get('location')  # Extract 'location' from the dictionary
        description = event_item.get('meeting_notes_html')
        # Host Details        
        host_email = event_item.get('event_memberships', [{}])[0].get('user_email')  # Assuming first membership is the host
        host_name = event_item.get('event_memberships', [{}])[0].get('user_name')
        host_uri = event_item.get('event_memberships', [{}])[0].get('user')

        host = self.env['res.users'].search(['|',('email', '=', host_email),('calendly_uri', '=', host_uri)], limit=1)
        if not host:
            host = self._create_calendly_host(host_email,host_name,host_uri)  # Implement _create_host method to create a new user

    
        # Convert start_time and end_time to datetime objects
        start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    
        if name and uri and start_time and end_time:
            return {
                'name': name,
                'calendly_uri': uri,
                'start': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'stop': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'location': location,
                'description': description,
                'user_id': host.id,
                # Add other fields as needed
            }
        else:
            return None

    def _create_calendly_host(self, host_email,host_name, host_uri):
        # Create a new user in Odoo with the provided email as the host
        # Example:
        host = self.env['res.users'].create({
            'name': host_name,
            'email': host_email,
            'calendly_uri': host_uri,
            'login': host_email,
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]  # Assign the user to the 'Portal' group
        })
        host.sudo().action_reset_password()
        return host
