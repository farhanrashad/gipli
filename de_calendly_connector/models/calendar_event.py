# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
from odoo import http, _
from odoo.http import request
import json

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    def test_users(self):
        CalendlyEventType = self.env['calendly.event.type']
        
        company_id = self.env.user.company_id
        user_data = company_id.get_current_user()
        user_uri = user_data['resource']['uri']

        #user_data = company_id.get_current_user()
        #user_uri = user_data['resource']['uri']

        event_types = company_id.get_event_types(organization=False, user=user_uri)

        if event_types:
            CalendarEventType = self.env['calendly.event.type']
        
            for event_type in event_types['collection']:
                event_type_uri = event_type['uri']
                existing_event_type = CalendarEventType.search([('uri', '=', event_type_uri)], limit=1)
        
                event_type_data = {
                    'name': event_type['name'],
                    'description': event_type.get('description_plain', ''),
                    'duration': event_type['duration'],
                    #'scheduling_url': event_type['scheduling_url'],
                    'uri': event_type_uri,
                    #'location': event_type['locations']['kind'],
                    #'company_id': company_id.id,
                }
                # Check if 'locations' key exists and is not None
                if 'locations' in event_type and event_type['locations'] is not None:
                    # Get the first location from the list and set it as the location for simplicity
                    # You can modify this logic to handle multiple locations if needed
                    first_location = event_type['locations'][0]
                    event_type_data['location'] = first_location['kind']
                else:
                    event_type_data['location'] = ''  # Set default location to blank
        
                if existing_event_type:
                    # Update existing event type if it already exists in Odoo
                    existing_event_type.write(event_type_data)
                else:
                    # Create new event type if it doesn't exist in Odoo
                    CalendarEventType.create(event_type_data)


    def temp(self):
        data_str = json.dumps(event_types, indent=4)
        raise UserError(data_str)
        
        raise UserError(company_id.get_current_user())

        access_token = company_id.calendly_access_token
        refresh_token = company_id.calendly_refresh_token

        # Schedule Events List
        if access_token:
            # Get list of event types
            response = requests.get(
                'https://api.calendly.com/scheduled_events', 
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                }
            )
            #user_data = response.json()
            #user_data_str = json.dumps(user_data, indent=4)
            #raise UserError(user_data_str)
            
        #raise UserError(access_token)
        
        if access_token:
            # Get list of event types
            event_types_response = requests.get(
                'https://api.calendly.com/users/me', 
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                }
            )

            user_data = event_types_response.json()
            name = user_data['resource']['name']
            #raise UserError(name)


            user_data = event_types_response.json()
            user_data_str = json.dumps(user_data, indent=4)
            raise UserError(user_data_str)