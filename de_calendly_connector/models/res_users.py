# -*- coding: utf-8 -*-

import requests
from odoo import api, fields, models, Command
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import json
CALENDLY_BASE_URL = 'https://api.calendly.com'

class ResUsers(models.Model):
    _inherit = 'res.users'

    calendly_uri = fields.Char(string='Calendly User URI', readonly=True)
    calendly_org_uri = fields.Char(string='Calendly Org URI', readonly=True)
    
    @api.model
    def _sync_all_calendly_events(self):
        """ Cron job """
        company_id = self.env.user.company_id
        
        current_user = company_id._get_calendly_current_user()
        #data_str = json.dumps(current_user, indent=4)
        #raise UserError(data_str)
        org_uri = current_user['resource']['current_organization']

        self._sync_calendly_users(org_uri)
        self._sync_calendly_events(org_uri)

    def _sync_calendly_users(self,org_uri):
        company_id = self.env.user.company_id
        members = company_id._get_calendly_organization_memberships(org_uri,user=False)
        members_collection_data = members.get('collection', [])
        if not members_collection_data:
            raise ValueError('No data found in the collection')
    
        users = []
        for member in members_collection_data:
            user_info = member.get('user')
            if user_info:
                users.append(user_info)
    
        if not users:
            raise ValueError('No user data found in the collection')
    
        company_id._update_calendly_memberships(users)

    def _sync_calendly_events(self,org_uri):
        company_id = self.env.user.company_id
        events = company_id._get_calendly_scheduled_events(org_uri, user=False)
        collection_data = events.get('collection', [])
        if not collection_data:
            raise ValueError('No data found in the collection')
        
        company_id._update_calendly_events(collection_data)
    
        
