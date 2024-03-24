# -*- coding: utf-8 -*-

import requests
from odoo import api, fields, models, Command
from odoo.exceptions import UserError
from datetime import datetime, timedelta

CALENDLY_BASE_URL = 'https://api.calendly.com'

class ResUsers(models.Model):
    _inherit = 'res.users'

    calendly_uri = fields.Char(string='Calendly User URI')
    calendly_org_uri = fields.Char(string='Calendly Org URI')
    
    @api.model
    def _sync_all_calendly_events(self):
        """ Cron job """
        #users = self.env['res.users'].search([('active','=',True)])
        pass