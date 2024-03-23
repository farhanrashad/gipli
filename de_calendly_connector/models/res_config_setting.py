# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    calendly_client_id = fields.Char(related="company_id.calendly_client_id", readonly=False)
    calendly_client_secret = fields.Char(related="company_id.calendly_client_secret", readonly=False)

    calendly_generated_access_token = fields.Boolean(related="company_id.calendly_generated_access_token")

    def action_generate_access_token(self):

        client_id = self.calendly_client_id
        client_secret = self.calendly_client_secret
        redirect_url = "https://g2020-dev17-12386251.dev.odoo.com/calendly/callback"

        url = (
            "https://auth.calendly.com/oauth/authorize?response_type=code"
            "&client_id={}&redirect_uri={}"
        ).format(client_id, redirect_url)
        return {
            "type": 'ir.actions.act_url',
            "url": url,
            "target": "current"
        }