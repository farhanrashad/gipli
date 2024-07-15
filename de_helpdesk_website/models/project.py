# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons.http_routing.models.ir_http import slug


class Project(models.Model):
    _inherit = 'project.project'

    is_published = fields.Boolean("Web Published")

    website_id = fields.Many2one('website', domain="[('company_id', '=?', company_id)]", compute='_compute_website_id', store=True, readonly=False)
    website_url = fields.Char('Url', compute='_compute_website_url',)

    @api.depends('company_id')
    def _compute_website_id(self):
        for team in self:
            team.website_id = team.company_id.website_id

    def _compute_website_url(self):
        for team in self:
            team.website_url = "/helpdesk/%s" % slug(team)
            
    def open_website_url(self):
        return self.env['website'].get_client_action(self.website_url, website_id=self.website_id.id)