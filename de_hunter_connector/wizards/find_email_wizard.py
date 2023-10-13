# -*- coding: utf-8 -*-

import requests
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import pprint

from urllib.parse import urlparse

class HunterFindEmailWizard(models.TransientModel):
    _name = "hunter.find.email.wizard"
    _description = 'Find Email Wizard'

    api_type = fields.Selection([
        ('domain', 'Domain Search'), ('company', 'Company Search'),
        ('email_domain', 'Find Emails by Domain'), ('email_company', 'Find Emails by Company'),
        ('email_name', 'Find Email by Name'), ('email_verify', 'Verify Email')
    ], required=True, string="Operation Type", default='domain')

    domain = fields.Char(string='Domain')
    company_name = fields.Char(string='Company Name')
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    full_name = fields.Char(string='Full Name')
    email = fields.Char(string='Email')
    

    def action_find_emails(self):
        pass