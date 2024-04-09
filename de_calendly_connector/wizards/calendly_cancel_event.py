# -*- coding: utf-8 -*-

from odoo import fields, models, _, api, Command, SUPERUSER_ID, modules
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html_escape
from odoo.tools import date_utils
import json

class CalendlyCancelEventWizard(models.TransientModel):
    _name = 'calendly.cancel.event.wizard'
    _description = 'Calendly Cancel Event Wizard'

    cancel_type = fields.Selection([
        ('calendly', 'Cancel on Calendly Only'),  
        ('both', 'Cancel on both Calendly and Odoo'),  
    ], 
        string='Type', required=True, default="calendly",
    )
    reason_cancel = fields.Char(string='Reason for Cancel', required=True) 
    event_ids = fields.Many2many(
        string="events to cancel",
        comodel_name='calendar.event',
        default=lambda self: self.env.context.get('active_ids'),
        relation='calendar_event_calendly_mass_cancel_wizard_rel',
    )

    def cancel_calendly_event(self):
        for event in self.event_ids:
            if self.cancel_type == 'calendly':
                event = self.env.user.company_id.sudo()._calendly_cancel_event(event.calendly_uri,self.reason_cancel)
                data_str = json.dumps(event, indent=4)
                raise UserError(data_str)
                event.message_post(body=f"Event cancelled on calendly due to : {self.reason_cancel}")
            else:
                event.message_post(body=f"Event cancelled due to : {self.reason_cancel}")
                event.action_mass_archive("all_events")
                
