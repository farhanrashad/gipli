# -*- coding: utf-8 -*-

from odoo import fields, models, _, api, Command, SUPERUSER_ID, modules
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html_escape
from odoo.tools import date_utils

class SchedulePostWizard(models.TransientModel):
    _name = 'sm.schedule.post.wizard'
    _description = 'Schedule Post Wizard'

    date_scheduled = fields.Datetime('Scheduled Date', required=True)

    def action_schedule(self):
        pass