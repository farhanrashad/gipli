# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
from odoo import http, _
from odoo.http import request
import json

import logging

_logger = logging.getLogger(__name__)


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    calendly_uri = fields.Char(string='Calendly URI', readonly=True)
    is_calendly = fields.Boolean(string='Calendly Event',
                                 compute='_compute_calendly',
                                 store=True,
                                )
    calendly_cancel_reason = fields.Char('Calendly Cancel Reason', readonly=True)

    # Compute Methods
    @api.depends('calendly_uri')
    def _compute_calendly(self):
        for record in self:
            if record.calendly_uri:
                record.is_calendly = True
            else:
                record.is_calendly = False

    def write(self, values):
        if 'active' in values and not values.get('active'):
            for record in self:
                record.env.user.company_id.sudo()._calendly_cancel_event(record.calendly_uri, 'test reason')
            values.update({
                'calendly_uri': False,
                'is_calendly': False,
            })
        return super(CalendarEvent, self).write(values)
        
    def action_mass_archive(self, recurrence_update_setting):
        raise UserError('hello')
        res = super(CalendarEvent, self).action_mass_archive(recurrence_update_setting)
        self.env.user.company_id.sudo()._calendly_cancel_event(self.calendly_uri,'test reason')
        self.write({
            'calendly_uri': False,
            'is_calendly': False,
        })
        
    # Actions
    def button_calendly_cancel(self):
        self.ensure_one()
        return {
            'name': 'Cancel Events',
            'view_mode': 'form',
            'res_model': 'calendly.cancel.event.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        
        #raise UserError(self.user_id.calendly_uri)
        #event = self.env.user.company_id.sudo()._get_calendly_event(self.calendly_uri)
        #event = self.env.user.company_id.sudo()._calendly_cancel_event(self.calendly_uri,'test reason')
        #data_str = json.dumps(event, indent=4)
        #raise UserError(data_str)
        
    def action_get_schedule_events2(self):
        self.env.user.sudo()._sync_all_calendly_events()

    def action_get_schedule_events(self):
        company_id = self.env.user.company_id
        token = company_id._refresh_calendly_access_token()
        
        current_user = company_id.get_current_user()
        org_uri = current_user['resource']['current_organization']

        subscriptions = company_id._get_calendly_webhook_subscriptions(org_uri, user=False)
        
        data_str = json.dumps(subscriptions, indent=4)
        raise UserError(data_str)
        
        subscriptions = company_id._create_calendly_webhook_subscription(
            uri='/calendly/event/create',
            organization=org_uri,
            user=False,
            events=['invitee.created']
        )

        #subscriptions = company_id._get_calendly_webhook_subscriptions(org_uri, user=False)
        
        #data_str = json.dumps(subscriptions, indent=4)
        #raise UserError(data_str)
        
    
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
        current_user = company_id._get_calendly_current_user()
        org_uri = current_user['resource']['current_organization']

        #raise UserError(company_id._get_calendly_access_token())
        #refresh_token = company_id._generate_calendly_refresh_token()

        members = company_id._get_calendly_organization_memberships(org_uri, user=False)

        #subscriptions = company_id._get_calendly_webhook_subscriptions(org_uri, user=False)
        data_str = json.dumps(members, indent=4)
        raise UserError(data_str)

    # action for calendly 
    @api.model
    def handle_webhook_event(self, payload):
        # Process the incoming payload from Calendly and create calendar.event records
        _logger.info(f"Processing Calendly Event: {payload}")
        event_data = payload.get('payload', {})
        # Extract relevant data from event_data and create calendar.event records
        # Example: Create a calendar event with a name and start date
        self.env['calendar.event'].create({
            'name': event_data.get('event_name', ''),
            'start': event_data.get('event_time', ''),
            # Add other fields as needed
        })