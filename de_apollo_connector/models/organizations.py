# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _
from odoo.exceptions import UserError, AccessError
from odoo.tools import html_escape as escape

import requests
import json

class ApolloComapniesResults(models.Model):
    _name = 'apl.companies'
    _description = 'Apollo Companies'

    apl_id = fields.Char('ID')
    name = fields.Char('Name')
    website_url = fields.Char('Website')
    blog_url = fields.Char('Blog')
    angellist_url = fields.Char('Angel List')
    linkedin_url = fields.Char('LinkedIn')
    linkedin_uid = fields.Char('LinkedIn UID')
    twitter_url = fields.Char('Twitter')
    facebook_url = fields.Char('Facebook')
    alexa_ranking = fields.Integer('Alexa Ranking')
    founded_year = fields.Integer('Founded Year')
    logo_url = fields.Char('Logo')
    primary_domain = fields.Char('Primary Domain')

    def action_custom_button(self):
        pass