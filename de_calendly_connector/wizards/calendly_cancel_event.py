# -*- coding: utf-8 -*-

from odoo import fields, models, _, api, Command, SUPERUSER_ID, modules
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html_escape
from odoo.tools import date_utils

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
        pass