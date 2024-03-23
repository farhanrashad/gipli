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

        access_token = company_id.calendly_access_token
        refresh_token = company_id.calendly_refresh_token

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
            raise UserError(name)

            
            # Parse the JSON response
            parsed_response = json.loads(event_types_response)
            
            # Extract the name field
            uname = parsed_response['resource']['name']


            user_data = event_types_response.json()
            user_data_str = json.dumps(user_data, indent=4)
            raise UserError(uname)