# -*- coding: utf-8 -*-

import requests
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class APLPeopleSearchWizard(models.TransientModel):
    _name = "apl.people.search.wizard"
    _description = 'Search People Wizard'

    apl_instance_id = fields.Many2one('apl.instance')
    name = fields.Char(string='Name')
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
            #"q_organization_domains": "apollo.io\ngoogle.com",
            "page" : 2,
            "person_titles" : ["manager"]
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
            organization_data = data.get('organization', [])
    
        person_values = {}

        self.env['apl.companies'].search([('create_uid', '=', self.env.user.id)]).sudo().unlink()
        self.env['apl.people'].search([('create_uid', '=', self.env.user.id)]).sudo().unlink()
        self.env['apl.people.employment'].search([('create_uid', '=', self.env.user.id)]).sudo().unlink()
        
        for person_data in people_data:
            person_values = {
                'apl_id': person_data.get('id'),
                'first_name': person_data.get('first_name'),
                'last_name': person_data.get('last_name'),
                'name': person_data.get('name'),
                'organization_id': person_data.get('organization_id'),
                'title': person_data.get('title'),
                'email': person_data.get('email'),
                'email_status': person_data.get('email_status'),
                'linkedin_url': person_data.get('linkedin_url'),
                'twitter_url': person_data.get('twitter_url'),
                'github_url': person_data.get('github_url'),
                'facebook_url': person_data.get('facebook_url'),
                'photo_url': person_data.get('photo_url'),
                'country': person_data.get('country'),
                'state': person_data.get('state'),
                'city': person_data.get('city'),
                # Map other fields from JSON to your Odoo model fields
            }
            
            person = self.env['apl.people'].create(person_values)

            # Organization / Company Date
            organization_data = person_data.get('organization')
            if organization_data:
                organization_values = {
                    'name': organization_data.get('name'),
                    'website_url': organization_data.get('website_url'),
                    'blog_url': organization_data.get('blog_url'),
                    'angellist_url': organization_data.get('angellist_url'),
                    'linkedin_url': organization_data.get('linkedin_url'),
                    'linkedin_uid': organization_data.get('linkedin_uid'),
                    'twitter_url': organization_data.get('twitter_url'),
                    'facebook_url': organization_data.get('facebook_url'),
                    'alexa_ranking': organization_data.get('alexa_ranking'),
                    'founded_year': organization_data.get('founded_year'),
                    'logo_url': organization_data.get('logo_url'),
                    'primary_domain': organization_data.get('primary_domain'),
                }
                organization = self.env['apl.companies'].create(organization_values)

                # Associate the organization with the person
                person.write({'apl_people_company_id': organization.id})
                

            # Employement History
            employement_history_ids = person_data.get('employment_history', [])
            for employement_history_id in employement_history_ids:
                employment_values = {
                    'degree': employement_history_id.get('degree'),
                    'start_date': employement_history_id.get('start_date'),
                    'end_date': employement_history_id.get('end_date'),
                    'grade_level': employement_history_id.get('grade_level'),
                    'kind': employement_history_id.get('kind'),
                    'major': employement_history_id.get('major'),
                    'description': employement_history_id.get('description'),
                    'apl_people_id': person.id,
                }
                employement = self.env['apl.people.employment'].create(employment_values)

                # Associate the Employment with the person
                person.write({'people_employment_history_ids': [(4, employement.id)]})
                
        # Return an action to open a new form view
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'name': _('Search Results'),
            'res_model': 'apl.people',
            'context': {'create': False, 'edit': False},  # Add the context here

        }
        return action


