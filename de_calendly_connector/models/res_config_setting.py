# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import requests
from odoo.exceptions import UserError
import json

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _get_base_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/'
        return base_url

    is_calendly = fields.Boolean(related='company_id.is_calendly', readonly=False)
    calendly_client_id = fields.Char(related="company_id.calendly_client_id", readonly=False)
    calendly_client_secret = fields.Char(related="company_id.calendly_client_secret", readonly=False)
    calendly_webhook_signing_key = fields.Char(related="company_id.calendly_webhook_signing_key", readonly=False)
    
    calendly_generated_access_token = fields.Boolean(related="company_id.calendly_generated_access_token")
    calendly_callback = fields.Char(related="company_id.calendly_callback", readonly=False)
    base_url = fields.Char(string='Base URL', 
                           default=lambda s: s._get_base_url(),
                           readonly=True,
                          )
    calendly_callback_uri = fields.Char(related="company_id.calendly_callback_uri")
    
    def action_generate_access_token(self):
        client_id = self.calendly_client_id
        client_secret = self.calendly_client_secret
        redirect_url = self.base_url + str(self.calendly_callback)
        self.calendly_callback_uri = redirect_url

        url = (
            "https://auth.calendly.com/oauth/authorize?response_type=code"
            "&client_id={}&redirect_uri={}"
        ).format(client_id, redirect_url)

        #cb = '/' + self.calendly_callback
        #response = requests.post(self.base_url + cb, data={'url_string': redirect_url})
        #raise UserError(response)
        
        return {
            "type": 'ir.actions.act_url',
            "url": url,
            #"target": "current"
        }