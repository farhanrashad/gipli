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
        

    def action_get_schedule_events(self):
        user_id = self.env.user
        user_id._sync_all_calendly_events()
        
    
    def test_users(self):
        company_id = self.env.user.company_id
        #current_user = company_id._get_calendly_current_user()
        #org_uri = current_user['resource']['current_organization']

        #raise UserError(company_id._get_calendly_access_token())
        refresh_token = company_id._generate_calendly_refresh_token()

        #members = company_id._get_calendly_organization_memberships(org_uri, user=False)
        #events = company_id._get_calendly_scheduled_events(org_uri, user=False)

        #subscriptions = company_id._get_calendly_webhook_subscriptions(org_uri, user=False)
        #subscription = company_id._create_calendly_webhook_subscription('/calendly/events',organization=org_uri, user=False)
        data_str = json.dumps(refresh_token, indent=4)
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