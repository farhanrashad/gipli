# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
from urllib.parse import urlencode, urlparse

class CalendlyInstance(models.Model):
    _name = 'cal.instance'
    _description = 'Calendly Instance'

    name = fields.Char(string='Name', required=True, readonly=False)
    client_id = fields.Char(string='Client ID', required=True)
    client_secret = fields.Char(string='Client secret', required=True)
    url = fields.Char(string='URL', required=True, readonly=False)
    url_sample = fields.Char(default='https://api.calendly.com/')
    access_token = fields.Char(string='Access Token')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, default=lambda self: self.env.company)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('verified', 'Verified'),
        ('active', 'Active')],
        string='Status', default='draft', required=True
    )

    # operations fields
    cal_date_import_contacts = fields.Datetime(string='Contacts import date')
    cal_date_import_accounts = fields.Datetime(string='Accounts import date')
    cal_date_import_leads = fields.Datetime(string='Leads import date')
    cal_date_export_contacts = fields.Datetime(string='Contacts export date')
    cal_date_export_leads = fields.Datetime(string='Leads export date')

    def button_draft(self):
        self.write({'state': 'draft'})

    def button_confirm(self):
        self.write({'state': 'active'})

    @api.model
    def _get_base_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return base_url or ''

    @api.model
    def _generate_redirect_uri(self):
        base_url = self._get_base_url()
        return base_url + '/calendly/callback'

    def _get_access_token(self, authorization_code):
        token_data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self._generate_redirect_uri(),
        }
        token_url = 'https://auth.calendly.com/oauth/token'
        response = requests.post(token_url, data=token_data)
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            error_message = response.json().get('error_description', 'Unknown error')
            raise UserError(error_message)

    def _test_connection(self):
        authorize_url = 'https://calendly.com/oauth/authorize'
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self._generate_redirect_uri(),
            #'scope': 'read write'
        }
        authorization_url = authorize_url + '?' + urlencode(params)
        return {
            'type': 'ir.actions.act_url',
            'url': authorization_url,
            'target': 'new',
        }

    def connection_test(self):
        return self._test_connection()

    def _parse_redirect_uri(self, redirect_uri):
        parsed_uri = urlparse(redirect_uri)
        return parsed_uri.query.split('code=')[-1]

    def button_confirm_connection(self):
        authorization_code = self._parse_redirect_uri(self.env.context.get('base_url'))
        access_token = self._get_access_token(authorization_code)
        self.write({'state': 'verified'})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError("You cannot delete a record with a state other than 'draft'.")
        return super(CalendlyInstance, self).unlink()
