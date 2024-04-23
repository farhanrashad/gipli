# -*- coding: utf-8 -*-

import requests
from odoo import models, fields
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import json
import base64
from urllib.parse import urlencode

import http.client

CALENDLY_BASE_URL = 'https://api.calendly.com'

class ResCompany(models.Model):
    _inherit = 'res.company'

    is_calendly = fields.Boolean('Calendly')
    calendly_client_id = fields.Char(string='Client ID')
    calendly_client_secret = fields.Char(string='Client secret')
    calendly_webhook_signing_key = fields.Char(string='Webhook signing key')
        
    calendly_access_token = fields.Char(string='Access Token')
    calendly_refresh_token = fields.Char(string='Refresh Token')
    calendly_token_validity = fields.Datetime('Token Validity', copy=False)
    calendly_generated_access_token = fields.Boolean(string='Access Token Generated')

    def _generate_calendly_token(self, code):
        redirect_uri = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/calendly/oauth'
        data = {
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        client_id_secret = str(
                self.calendly_client_id + ":" + self.calendly_client_secret).encode(
                'utf-8')
        client_id_secret = base64.b64encode(client_id_secret).decode('utf-8')
        response = requests.post(
                'https://auth.calendly.com/oauth/token', data=data,
                headers={
                    'Authorization': 'Basic ' + client_id_secret,
                    'content-type': 'application/x-www-form-urlencoded'})
        # self.write(self._prepare_calendly_token_values(response))
        return self._handle_response(response)

    def _generate_calendly_refresh_token(self):
        #company_ids = self.env['res.company'].search([('active','=',True)])
        company_id = self
        payload = {}
        url = 'https://auth.calendly.com/oauth/token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': "application/json",
        }
        #for company_id in company_ids:
        #    if company_id:
        payload = {
                    'grant_type': 'refresh_token',
                    'refresh_token': company_id.calendly_refresh_token,
                    'client_id': company_id.calendly_client_id,
                    'client_secret': company_id.calendly_client_secret
        }
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()
    
        company_id.write({
            'calendly_access_token': data.get('access_token'),
            #'calendly_refresh_token': data.get('refresh_token'),
            'calendly_token_validity': fields.Datetime.now() + timedelta(seconds=data.get('expires_in')),
        })
        return data

    def _get_calendly_access_token(self):
        if self.calendly_token_validity < fields.Datetime.now():
            self._generate_calendly_refresh_token()
        access_token = self.calendly_access_token
        return access_token
            
    def _get_calendly_api_header(self):
        access_token = self._get_calendly_access_token
        return {
            'Authorization': f'Bearer {access_token}', 
            'Accept': 'application/json'
        }
        

    

    def _handle_response(self, response):
        return response.json()
        #if response.status_code == 401:
            # Handle token refresh here if needed
        #    raise UserError('Unauthorized. Token refresh logic goes here.')
        #elif not response.ok:
        #    raise UserError(f'Error: {response.status_code} - {response.text}')
        #else:
        #    return response.json()

    

    def _get_calendly_current_user(self):
        access_token = self._get_calendly_access_token()
        url = 'https://api.calendly.com/users/me'
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        return data
        
        #url = f'{CALENDLY_BASE_URL}/users/me'
        #params = {}
        #headers = self._get_calendly_api_header()
        #response = requests.get(url, params=params, headers=headers)
        #return self._handle_response(response)

    def _get_calendly_users(self, user=None):
        url = f'{CALENDLY_BASE_URL}/user'
        params = {}
        if user:
            params['user'] = user
        headers = self._get_calendly_api_header()
        response = requests.get(url, params=params, headers=headers)
        return self._handle_response(response)
        
    def get_event_types(self, organization=None, user=None):
        url = f'{CALENDLY_BASE_URL}/event_types'
        params = {}
        if organization:
            params['organization'] = organization
        if user:
            params['user'] = user
        headers = self._get_calendly_api_header()
        response = requests.get(url, params=params, headers=headers)
        return self._handle_response(response)

    # Calendly Membership
    def _get_calendly_organization_memberships(self, organization=None, user=None):
        access_token = self._get_calendly_access_token()
        url = 'https://api.calendly.com/organization_memberships'
        params = {}
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        if organization:
            params['organization'] = organization
        if user:
            params['user'] = user
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        return data

    
    def _update_calendly_memberships(self, collection_data):
        user_ids = self.env['res.users']
        data_str = json.dumps(collection_data, indent=4)
        #raise UserError(data_str)
        
        #for item in collection_data:
        #member = item.get('user', [])
        users = self._create_update_user(collection_data)
    
    # Calendly Events
    def _get_calendly_scheduled_events(self, organization=None, user=None):
        access_token = self._get_calendly_access_token()
        url = 'https://api.calendly.com/scheduled_events'
        params = {}
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        if organization:
            params['organization'] = organization
        if user:
            params['user'] = user
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        return data
        
        #url = f'{CALENDLY_BASE_URL}/scheduled_events'
        #params = {}
        #if organization:
        #    params['organization'] = organization
        #if user:
        #    params['user'] = user

        #headers = self._get_calendly_api_header()
        #response = requests.get(url, params=params, headers=headers)
        #return self._handle_response(response)

    def _get_calendly_event(self, uuid=None, user=None):
        base_url = 'https://api.calendly.com'
        endpoint = f'/scheduled_events/{uuid}'

        headers = self._get_calendly_api_header()
        response = requests.get(base_url + endpoint, headers=headers)
        return self._handle_response(response)
        
    def _calendly_cancel_event(self, uuid, reason=None):
        base_url = 'https://api.calendly.com'
        endpoint = f'/scheduled_events/{uuid}/cancellation'
        url = f"{base_url}{endpoint}"
        headers = self._get_calendly_api_header()
        headers['Content-Type'] = 'application/json'
    
        payload = {}
        if reason:
            payload['reason'] = reason
    
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an error for non-2xx responses
            return response.json()  # Return JSON response as Python dictionary
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    # CRUD for Calendly Events
    def _update_calendly_events(self, collection_data):
        calendar_event_obj = self.env['calendar.event']
        for item in collection_data:
            if item.get('status') == 'active':
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

        # Event Host
        event_members = event_item.get('event_memberships', [])
        #host = self._create_update_user(event_members)
        #host.sudo().action_reset_password()
        users = []
        for member in event_members:
            member_uri = member.get('user')
            user_info = member_uri.split('/')[-1]
            if user_info:
                users.append(user_info)
        host = self.env['res.users'].search([('calendly_uri','in',users)],limit=1)
                
    
        # Convert start_time and end_time to datetime objects
        start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')

        # Event Guests
        event_guests = event_item.get('event_guests', [])
        attendees_ids = self._create_update_attendees(event_guests)
        #partner_ids = [(4, attendee.id) for attendee in attendees]

        partner_ids = [(4, host.partner_id.id)]  # Add the host.partner_id.id to the partner_ids list
        if attendees_ids:
            partner_ids += [(4, attendee_id) for attendee_id in attendees_ids.ids]
        
        
        if name and uri and start_time and end_time:
            return {
                'name': name,
                'calendly_uri': uri.split('/')[-1],
                'start': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'stop': end_time.strftime('%Y-%m-%d %H:%M:%S'),
                'location': location,
                'description': description,
                'user_id': host.id,
                'partner_ids': partner_ids,
                'partner_id': self.env.user.partner_id.id,
            }
        else:
            return None

    def _create_update_user(self, members):
        user = self.env['res.users']
        for member in members:
            email = member.get('email')
            #name = member.get('user_name')
            #uri = member.get('user')
            if email:
                user |= self._prepare_user_values(member)
        return user
    
    def _prepare_user_values(self, member):
        url = member.get('uri')
        user = self.env['res.users'].search(['|', ('email', '=', member.get('email')), ('calendly_uri', '=', member.get('uri'))], limit=1)
        if user:
            # Update existing user record if email and uri are found
            user.write({
                'calendly_uri': url.split('/')[-1],
                #'name': member.get('name'),
                #'login': member.get('name'),
            })
        else:
            # Create new user record if email and uri are not found
            user = self.env['res.users'].create({
                'name': member.get('name'),
                'email': member.get('email'),
                'calendly_uri': url.split('/')[-1],
                'login': member.get('email'),
                'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
            })
            user.sudo().action_reset_password()
        return user or False
        
    def _create_update_attendees(self, event_guests):
        attendees = self.env['res.partner']
        for guest in event_guests:
            email = guest.get('email')
            if email:
                attendees |= self._prepare_attendees_values(email)
        return attendees

    def _prepare_attendees_values(self, email):
        partner = self.env['res.partner'].search([('email', '=', email)], limit=1)
        if partner:
            # Update existing partner record if email is found
            partner.write({
                #'email': email,
                #'calendly_uri': uri,
                'type': 'contact',
                'name': email.split('@')[0], 
            })
        else:
            # Create new partner record if email is not found
            partner = self.env['res.partner'].create({
                'name': email.split('@')[0], 
                'email': email,
                'type': 'contact',
            })
        return partner or False  # Return the existing or newly created partner record

    # Webhook
    def _create_calendly_webhook_subscription(self, uri, organization=None, user=None, events=[]):
        url = f'{CALENDLY_BASE_URL}/webhook_subscriptions'
        client_id = self.calendly_client_id
        client_secret = self.calendly_client_secret
        conn = http.client.HTTPSConnection("api.calendly.com")
        payload = {
            "url": self.env['ir.config_parameter'].sudo().get_param('web.base.url') + uri,
            "events": [
                "invitee.created",
                "invitee.canceled",
                "invitee_no_show.created"
              ],
            "scope": "organization",
            "signing_key": self.calendly_webhook_signing_key,
        }
        if organization:
            payload['organization'] = organization
        if user:
            payload['user'] = user
        client_id_secret = str(client_id + ":" + client_secret).encode('utf-8')
        client_id_secret = base64.b64encode(client_id_secret).decode('utf-8')
        
        #raise UserError(client_id_secret)
        headers = {
            'Authorization': 'Bearer ' + self.calendly_access_token,
            'Content-Type': 'application/json'  # Changed content type to JSON
        }
        json_payload = json.dumps(payload)  # Convert payload to JSON format
        conn.request("POST", "/webhook_subscriptions", json_payload, headers)  # Send JSON payload
        res = conn.getresponse()
        data = res.read()
        return data.decode("utf-8")

    def _get_calendly_webhook_subscriptions(self, organization=None, user=None):
        base_url = 'api.calendly.com'
        endpoint = '/webhook_subscriptions'
        conn = http.client.HTTPSConnection(base_url)
        params = {}
        if organization:
            params['organization'] = organization
        if user:
            params['user'] = user
        params['scope'] = 'organization'
        url = f"{endpoint}?{urlencode(params)}"  # Include parameters in the URL
        conn.request("GET", url, headers=self._get_calendly_api_header())
        res = conn.getresponse()
        data = res.read()
        json_data = json.loads(data.decode("utf-8"))
        return json_data

        
        #headers = self._get_calendly_api_header()
        #response = requests.get(url, params=params, headers=headers)
        #return self._handle_response(response)
