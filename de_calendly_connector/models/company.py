# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    calendly_client_id = fields.Char(string='Client ID')
    calendly_client_secret = fields.Char(string='Client secret')
    calendly_access_token = fields.Char(string='Access Token')
    calendly_refresh_token = fields.Char(string='Refresh Token')
    calendly_generated_access_token = fields.Boolean(string='Access Token Generated')