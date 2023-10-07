# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _
from odoo.exceptions import UserError, AccessError
from odoo.tools import html_escape as escape

import requests
import json

class ApolloPeopleResults(models.Model):
    _name = 'apl.people.results'
    _description = 'People Results'

    apl_id = fields.Char('ID')
    first_name = fields.Char('First Name')
    last_name = fields.Char('Last Name')
    name = fields.Char('Name')
    title = fields.Char('title')
    email = fields.Char('Email')
    email_status = fields.Char('email_status')
    linkedin_url = fields.Char('linkedin_url')
    twitter_url = fields.Char('twitter_url')
    github_url = fields.Char('github_url')
    facebook_url = fields.Char('facebook_url')
    photo_url = fields.Char('photo_url')
    
    

    def action_custom_button(self):
        pass

    def open_linkedin_profile(self):
        # Get the LinkedIn profile URL from a field in your model
        linkedin_profile_url = self.linkedin_url  # Replace with your field name
        if linkedin_profile_url:
            return {
                'type': 'ir.actions.act_url',
                'url': linkedin_profile_url,
                'target': 'new',
            }
    def open_twitter_profile(self):
        linkedin_profile_url = self.twitter_url  # Replace with your field name
        if linkedin_profile_url:
            return {
                'type': 'ir.actions.act_url',
                'url': linkedin_profile_url,
                'target': 'new',
            }
    def open_facebook_profile(self):
        # Get the LinkedIn profile URL from a field in your model
        linkedin_profile_url = self.facebook_url  # Replace with your field name
        if linkedin_profile_url:
            return {
                'type': 'ir.actions.act_url',
                'url': linkedin_profile_url,
                'target': 'new',
            }
    def open_github_profile(self):
        # Get the LinkedIn profile URL from a field in your model
        linkedin_profile_url = self.github_url  # Replace with your field name
        if linkedin_profile_url:
            return {
                'type': 'ir.actions.act_url',
                'url': linkedin_profile_url,
                'target': 'new',
            }