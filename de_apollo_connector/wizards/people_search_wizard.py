# -*- coding: utf-8 -*-

import requests
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class APLPeopleSearchWizard(models.TransientModel):
    _name = "apl.people.search.wizard"
    _description = 'Search People Wizard'

    apl_instance_id = fields.Many2one('apl.instance', required=True)
    name = fields.Char(string='Name', )
    job_titles = fields.Char(string='Job Titles')
    company_name = fields.Char(string='Company Name')
    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one('res.country.state', string='State', domain="[('country_id', '=', country_id)]")
    city = fields.Char(string='City')
    industry_keywords = fields.Char(string='Industry Keywords')
    no_of_employee = fields.Integer(string='No. of Employees')

    apl_page = fields.Integer('Page', required=True, help="Which page number from apollo to return. Defaults to 1")

    def action_search(self):
        url = self.apl_instance_id.url + 'mixed_people/search'
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json'
        }
        data = {
            "api_key": self.apl_instance_id.api_key,
            "q_organization_domains": "apollo.io\ngoogle.com",
            "page" : 1,
            "person_titles" : ["sales manager", "engineer manager"]
        }
        #response = requests.request("POST", url, headers=headers, json=data)

        #raise UserError(response.text)

        
        #data = json.loads(response.text)
        data = self.apl_instance_id.fetch_json_data('mixed_people/search', data)
        # Check if data is a list, and if it is, assign it to people_data
        if isinstance(data, list):
            people_data = data
        # If data is a dictionary, check if 'people' key exists and assign it to people_data
        elif isinstance(data, dict):
            people_data = data.get('people', [])
    
        #people_data = data.get('people', [])
        
        for person_data in people_data:
            person_values = {
                'apl_id': person_data.get('id'),
                'first_name': person_data.get('first_name'),
                'last_name': person_data.get('last_name'),
                'name': person_data.get('name'),
                'title': person_data.get('title'),
                'email': person_data.get('email'),
                'email_status': person_data.get('email_status'),
                'linkedin_url': person_data.get('linkedin_url'),
                'twitter_url': person_data.get('twitter_url'),
                'github_url': person_data.get('github_url'),
                'facebook_url': person_data.get('facebook_url'),
                'photo_url': person_data.get('photo_url'),
                # Map other fields from JSON to your Odoo model fields
            }
            self.env['apl.people.results'].unlink()
            person = self.env['apl.people.results'].create(person_values)

        # Return an action to open a new form view
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'name': _('Search Results'),
            'res_model': 'apl.people.results',
            'context': {'create': False, 'edit': False},  # Add the context here

        }
        return action


