# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _
from odoo.exceptions import UserError, AccessError
from odoo.tools import html_escape as escape

import requests
import json

class ApolloComapniesResults(models.Model):
    _name = 'apl.companies'
    _description = 'Apollo Companies'

    apl_id = fields.Char('ID', readonly=True)
    name = fields.Char('Name', readonly=True)
    website_url = fields.Char('Website', readonly=True)
    blog_url = fields.Char('Blog', readonly=True)
    angellist_url = fields.Char('Angel List', readonly=True)
    linkedin_url = fields.Char('LinkedIn', readonly=True)
    linkedin_uid = fields.Char('LinkedIn UID', readonly=True)
    twitter_url = fields.Char('Twitter', readonly=True)
    facebook_url = fields.Char('Facebook', readonly=True)
    alexa_ranking = fields.Integer('Alexa Ranking', readonly=True)
    founded_year = fields.Integer('Founded Year', readonly=True)
    logo_url = fields.Char('Logo')
    primary_domain = fields.Char('Primary Domain', readonly=True)

    apl_people_ids = fields.One2many('apl.people', 'apl_people_company_id', string="Peoples")


    def action_custom_button(self):
        pass