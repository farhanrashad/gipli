# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
from odoo import http, _
from odoo.http import request
import json

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    calendly_uri = fields.Char(string='Calendly URI')

    def action_get_schedule_events2(self):
        self.env.user.sudo()._sync_all_calendly_events()

    def action_get_schedule_events(self):
        company_id = self.env.user.company_id
        #raise UserError(company_id._get_base_url())
        #company_id._refresh_access_token()
        
    def action_get_schedule_events3(self):
        company_id = self.env.user.company_id
        
        current_user = company_id.get_current_user()
        org_uri = current_user['resource']['current_organization']

        events = company_id._get_calendly_scheduled_events(org_uri, user=False)

        collection_data = events.get('collection', [])
        if not collection_data:
            raise ValueError('No data found in the collection')
        
        company_id._update_calendly_events(collection_data)

        users = []
        for member in collection_data:
            user_info = member.get('event_memberships')
            if user_info:
                users.append(user_info)
        #raise UserError(users)
        member_data = events.get('collection', ['event_memberships'])
        data_str = json.dumps(users, indent=4)
        #raise UserError(data_str)
        
    
    def test_users(self):
        company_id = self.env.user.company_id
        
        current_user = company_id.get_current_user()
        org_uri = current_user['resource']['current_organization']

        subscriptions = company_id._get_calendly_webhook_subscriptions(org_uri, user=False)
        data_str = json.dumps(subscriptions, indent=4)
        raise UserError(data_str)