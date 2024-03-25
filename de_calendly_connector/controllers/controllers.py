# -*- coding: utf-8 -*-

import base64
import datetime
import requests
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import json

import logging

_logger = logging.getLogger(__name__)

class CalendlyCallbackController(http.Controller):

    @http.route('/calendly/oauth', type='http', auth='public', website=True)
    def handle_calendly_callback(self, **kw):

        company_id = request.env.user.company_id or http.request.env['res.users'].sudo().browse(
            user_id).company_id
        user_id = request.uid
        client_id = company_id.calendly_client_id
        client_secret = company_id.calendly_client_secret
        redirect_uri = request.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/calendly/oauth'

        #raise UserError(kw.get('code'))
        
        if kw.get('code'):
            #response = company_id._generate_calendly_token(kw.get('code'))
            #self._prepare_calendly_token_values(response)
            #raise UserError(response)
            data = {
                'code': kw.get('code'),
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
            cient_id_secret = str(
                client_id + ":" + client_secret).encode(
                'utf-8')
            cient_id_secret = base64.b64encode(cient_id_secret).decode('utf-8')
            response = requests.post(
                'https://auth.calendly.com/oauth/token', data=data,
                headers={
                    'Authorization': 'Basic ' + cient_id_secret,
                    'content-type': 'application/x-www-form-urlencoded'})

            #raise UserError(response.json())
            if response.json() and response.json().get('access_token'):
                company_id.write(self._prepare_calendly_token_values(response))
                #expires_in = response.json().get('expires_in')
                #new_token_validity = datetime.now() + timedelta(seconds=expires_in)
                #company_id.write({
                #    'calendly_access_token': response.json().get('access_token'),
                #    'calendly_refresh_token':  response.json().get('refresh_token'),
                #    'calendly_generated_access_token': True,
                #    'calendly_token_validity': new_token_validity,
                #})
                close_script = "<script>window.close();</script>"
                response_msg = {'success': True, 'close_script': close_script}
                return json.dumps(response_msg)
                #return "Authentication Success. You Can Close this window"
            else:
                raise UserError(
                    _('Something went wrong during the token generation.'
                      'Maybe your Authorization Code is invalid'))
                raise UserError(response.json().get('access_token'))
                
            #raise UserError(response)

    def _prepare_calendly_token_values(self, response):
        expires_in = response.json().get('expires_in')
        token_validity = datetime.now() + timedelta(seconds=expires_in)
        return {
            'calendly_access_token': response.json().get('access_token'),
            'calendly_refresh_token':response.json().get('refresh_token'),
            'calendly_token_validity':token_validity,
            'calendly_generated_access_token': True,
        }

    @http.route('/calendly/event/create', type='http', auth='public', website=True)
    def create_calendly_event(self, **kw):
        # Parse the incoming JSON data from Calendly
        try:
            data = json.loads(request.httprequest.data)
        except ValueError:
            return json.dumps({'error': 'Invalid JSON data'})

        # Extract relevant information from the Calendly event data
        event_title = data.get('title')
        event_start_time = data.get('start_time')
        event_end_time = data.get('end_time')
        event_description = data.get('description')
        # Add more fields as needed

        # Create the calendar.event record in Odoo
        event_vals = {
            'name': event_title,
            'start': event_start_time,
            'stop': event_end_time,
            'description': event_description,
            # Add more fields as needed
        }
        new_event = request.env['calendar.event'].sudo().create(event_vals)

        # Return a JSON response indicating success or failure
        if new_event:
            return json.dumps({'success': True, 'event_id': new_event.id})
        else:
            return json.dumps({'error': 'Failed to create event'})
        
    @http.route('/calendly/invitee/created', type='http', auth='public', website=True)
    def create_invitee_created(self, **kw):
        try:
            data = json.loads(request.httprequest.data)
        except ValueError:
            return json.dumps({'error': 'Invalid JSON data'})

        scheduled_event_uri = data.get('payload', {}).get('scheduled_event', {}).get('uri')
        if not scheduled_event_uri:
            return json.dumps({'error': 'Scheduled event URI not found'})

        # Extract the UUID from the schedule event URI
        calendly_uri = scheduled_event_uri.split('/')[-1]

        # Check if the event already exists
        existing_event = request.env['calendar.event'].sudo().search([('calendly_uri', '=', calendly_uri)], limit=1)

        # Prepare data for creating/updating the event
        event_data = {
            'calendly_uri': calendly_uri,
            'name': data.get('payload', {}).get('name', 'Event'),
            # Add more fields as needed
        }

        # If the event exists, update the partner_ids with the host from event_memberships
        if existing_event:
            host_uri = data.get('payload', {}).get('scheduled_event', {}).get('event_memberships', [{}])[0].get('user')
            if host_uri:
                host_email = host_uri.split('/')[-1]
                host_partner = request.env['res.partner'].sudo().search([('email', '=', host_email)], limit=1)
                if host_partner:
                    event_data['partner_ids'] = [(4, host_partner.id)]

            existing_event.write(event_data)
            return json.dumps({'success': True, 'event_id': existing_event.id})
        else:
            new_event = request.env['calendar.event'].sudo().create(event_data)
            if new_event:
                return json.dumps({'success': True, 'event_id': new_event.id})
            else:
                return json.dumps({'error': 'Failed to create event'})
            