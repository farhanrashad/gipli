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
        company_id = request.env.user.company_id or http.request.env['res.users'].sudo().browse(
            user_id).company_id
        user_id = request.uid
        client_id = company_id.discord_client_id
        client_secret = company_id.discord_client_secret
        redirect_uri = request.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/discord/oauth'

        #raise UserError(kw.get('code'))
        
        if kw.get('code'):
            data = {
                'code': kw.get('code'),
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
            cient_id_secret = str(
                client_id + ":" + client_secret).encode(
                'utf-8')
            cient_id_secret = base64.b64encode(cient_id_secret).decode('utf-8')
            response = requests.post(
                'https://auth.discord.com/oauth/token', data=data,
                headers={
                    'Authorization': 'Basic ' + cient_id_secret,
                    'content-type': 'application/x-www-form-urlencoded'})

            #raise UserError(response.json())
            if response.json() and response.json().get('access_token'):
                company_id.write(self._prepare_discord_token_values(response))
                close_script = "<script>window.close();</script>"
                response_msg = {'success': True, 'close_script': close_script}
                return json.dumps(response_msg)
                #return "Authentication Success. You Can Close this window"
            else:
                raise UserError(
                    _('Something went wrong during the token generation.'
                      'Maybe your Authorization Code is invalid'))
                raise UserError(response.json().get('access_token'))
                
            #raise UserError(response)

    def _prepare_discord_token_values(self, response):
        expires_in = response.json().get('expires_in')
        token_validity = datetime.now() + timedelta(seconds=expires_in)
        return {
            'discord_access_token': response.json().get('access_token'),
            'discord_refresh_token':response.json().get('refresh_token'),
            'discord_token_validity':token_validity,
            'discord_generated_access_token': True,
        }