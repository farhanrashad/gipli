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
        company_id = self.env.user.company_id
        user_data = company_id.get_current_user()
        name = user_data['resource']['name']
        raise UserError(name)
        
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