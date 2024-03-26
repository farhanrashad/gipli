# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import requests
from odoo.exceptions import UserError
import json

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _default_base_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/discord/oauth'
        return base_url

    is_discord = fields.Boolean(related='company_id.is_discord', readonly=False)
    discord_client_id = fields.Char(related="company_id.discord_client_id", readonly=False)
    discord_client_secret = fields.Char(related="company_id.discord_client_secret", readonly=False)
    discord_webhook_signing_key = fields.Char(related="company_id.discord_webhook_signing_key", readonly=False)
    
    discord_generated_access_token = fields.Boolean(related="company_id.discord_generated_access_token")
    
    display_discord_callback_uri = fields.Char(string='Base URL', 
                           default=lambda s: s._default_base_url(),
                           compute='_compute_discord_callback_url',
                           readonly=True,
                          )

    @api.depends('discord_client_id')
    def _compute_discord_callback_url(self):
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/discord/oauth'
        self.display_discord_callback_uri = url
            
    def action_generate_access_token(self):
        client_id = self.discord_client_id
        client_secret = self.discord_client_secret
        redirect_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/discord/oauth'
        

        url = (
            "https://auth.discord.com/oauth/authorize?response_type=code"
            "&client_id={}&redirect_uri={}"
        ).format(client_id, redirect_url)
        
        return {
            "type": 'ir.actions.act_url',
            "url": url,
            #"target": "current"
        }