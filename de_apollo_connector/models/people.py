# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _
from odoo.exceptions import UserError, AccessError
from odoo.tools import html_escape as escape

import requests
import json

class ApolloPeople(models.Model):
    _name = 'apl.people'
    _description = 'Apollo People'

    apl_id = fields.Char('ID', readonly=True)
    first_name = fields.Char('First Name', readonly=True)
    last_name = fields.Char('Last Name', readonly=True)
    name = fields.Char('Name', readonly=True)
    organization_id = fields.Char('Organization ID', readonly=True)
    title = fields.Char('Title', readonly=True)
    email = fields.Char('Email', readonly=True)
    email_status = fields.Char('Email Status', readonly=True)
    linkedin_url = fields.Char('LinkedIn', readonly=True)
    twitter_url = fields.Char('Twitter', readonly=True)
    github_url = fields.Char('Github', readonly=True)
    facebook_url = fields.Char('Facebook', readonly=True)
    photo_url = fields.Char('Photo', readonly=True)
    apl_people_company_id = fields.Many2one('apl.companies', string='Organization', readonly=True)
    country = fields.Char('Country', readonly=True)
    state = fields.Char('State', readonly=True)
    city = fields.Char('City', readonly=True)

    people_employment_history_ids = fields.One2many('apl.people.employment', 'apl_people_id', string="People")

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

class ApolloPeopleEmployment(models.Model):
    _name = 'apl.people.employment'
    _description = 'Apollo People Employement History'

    apl_people_id = fields.Many2one('apl.people', string='People', readonly=True)
    degree = fields.Char('Degree', readonly=True)
    start_date = fields.Date('Start Date', readonly=True)
    end_date = fields.Date('End Date', readonly=True)
    grade_level = fields.Char('Grade Level', readonly=True)
    kind = fields.Char('Kind', readonly=True)
    major = fields.Char('Major', readonly=True)
    description = fields.Text('Description', readonly=True)
    