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

    group_discord = fields.Boolean(string="Discord", implied_group='de_discord_connector.group_discuss_discord')
    discord_client_id = fields.Char(
        string='Discord Client ID',
        config_parameter='discord.client_id')
    discord_client_secret = fields.Char(
        string='Discord Client Secret',
        config_parameter='discord.client_secret')
    
    display_discord_callback_uri = fields.Char(string='Base URL', 
                           default=lambda s: s._default_base_url(),
                           compute='_compute_discord_callback_url',
                           readonly=True,
                        copy=False,
                          )

    @api.depends('discord_client_id')
    def _compute_discord_callback_url(self):
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/discord/oauth'
        self.display_discord_callback_uri = url
            
    def action_discord_generate_access_token(self):
        client_id = self.discord_client_id
        client_secret = self.discord_client_secret
        redirect_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/discord/oauth'
        scopes = 'identify'

        url = (
            "https://discord.com/oauth2/authorize?response_type=code"
            "&client_id={}&redirect_uri={}&scope={}"
        ).format(client_id, redirect_url, scopes)
        
        return {
            "type": 'ir.actions.act_url',
            "url": url,
            "target": 'self',  # Open in the same window
        }