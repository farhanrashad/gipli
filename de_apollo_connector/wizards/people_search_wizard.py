# -*- coding: utf-8 -*-
from odoo import api, fields, models


class APLPeopleSearchWizard(models.TransientModel):
    _name = "apl.people.search.wizard"
    _description = 'Apollo Search Wizard'

    name = fields.Char(string='Name', required=True)
    job_titles = fields.Char(string='Job Titles')
    company_name = fields.Char(string='Company Name')
    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one('res.country.state', string='State', domain="[('country_id', '=', country_id)]")
    city = fields.Char(string='City')
    industry_keywords = fields.Char(string='Industry Keywords')
    no_of_employee = fields.Integer(string='No. of Employees')

    def action_search(self):
        pass


