# -*- coding: utf-8 -*-

import base64
import datetime
import requests
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import json

import logging

_logger = logging.getLogger(__name__)

class DiscordCallbackController(http.Controller):
    @http.route('/discord/oauth', type='http', auth='public', website=True)
    def handle_discord_callback(self, **kw):
        user_id = request.uid
        client_id = request.env['ir.config_parameter'].sudo().get_param('discord.client_id')
        client_secret = request.env['ir.config_parameter'].sudo().get_param('discord.client_secret')
        redirect_uri = request.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/discord/oauth'
        API_ENDPOINT = 'https://discord.com/api/v10'
        
        if kw.get('code'):
            data = {
                'grant_type': 'authorization_code',
                'code': kw.get('code'),
                'redirect_uri': redirect_uri
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers, auth=(client_id, client_secret))
            response.raise_for_status()
            #return response.json()
            self._prepare_discord_token_values(response)
        # Redirect using Python code
        return request.redirect(request.httprequest.referrer or '/')
            

    def _prepare_discord_token_values(self, response):
        expires_in = response.json().get('expires_in')
        token_validity = datetime.now() + timedelta(seconds=expires_in)
        request.env['ir.config_parameter'].sudo().set_param('discord.access_token', response.json().get('access_token'))
        request.env['ir.config_parameter'].sudo().set_param('discord.refresh_token', response.json().get('refresh_token'))
        request.env['ir.config_parameter'].sudo().set_param('discord.token_validity', token_validity.strftime('%Y-%m-%d %H:%M:%S'))