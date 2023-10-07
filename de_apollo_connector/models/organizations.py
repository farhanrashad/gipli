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


    def action_open_people(self):
        people = self.mapped('apl_people_ids')
        action = self.env['ir.actions.actions']._for_xml_id('de_apollo_connector.action_apl_people')
        if len(people) > 1:
            action['domain'] = [('id', 'in', people.ids)]
        elif len(people) == 1:
            form_view = [(self.env.ref('de_apollo_connector.apl_people_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = people.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
