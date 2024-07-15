# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons.http_routing.models.ir_http import slug


class Project(models.Model):
    _inherit = 'project.project'

    is_published = fields.Boolean("Web Published", store=True,
                                  compute='_compute_is_published')

    website_id = fields.Many2one('website', domain="[('company_id', '=?', company_id)]", compute='_compute_website_id', store=True, readonly=False)
    website_url = fields.Char('Url', store=True,
                              compute='_compute_website_url',)

    @api.depends('module_helpdesk_website')
    def _compute_is_published(self):
        for record in self:
            record.is_published = record.module_helpdesk_website
            
    @api.depends('company_id')
    def _compute_website_id(self):
        for record in self:
            record.website_id = record.company_id.website_id

    @api.depends('is_published')
    def _compute_website_url(self):
        for record in self:
            record.website_url = "/support/%s" % slug(record)
            
    def open_website_url(self):
        #self._get_project_by_website_url('/support/support-desk-5')
        return self.env['website'].get_client_action(self.website_url, website_id=self.website_id.id)

    def _get_project_by_website_url(self, url):
        #raise UserError(url)
        project = self.env["project.project"].search([
            ('website_url', '=', url)
        ], limit=10)
        return project