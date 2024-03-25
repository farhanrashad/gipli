# -*- coding: utf-8 -*-

import base64
import datetime
import requests
from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError
from datetime import datetime, timedelta

import logging

_logger = logging.getLogger(__name__)

class CalendlyCallbackController(http.Controller):

    @http.route('/calendly/callback', type='http', auth='public', website=True)
    def handle_calendly_callback(self, **kw):

        company_id = request.env.user.company_id or http.request.env['res.users'].sudo().browse(
            user_id).company_id
        user_id = request.uid
        
        client_id = company_id.client_id
        client_secret = company_id.client_secret
        redirect_uri = "https://g2020-dev17-12386251.dev.odoo.com/calendly/callback"
        
        

        instance_id = http.request.env['cal.instance'].sudo().search([])
        
        if kw.get('code'):
            data = {
                'code': kw.get('code'),
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            }
            b64 = str(
                client_id + ":" + client_secret).encode(
                'utf-8')
            b64 = base64.b64encode(b64).decode('utf-8')
            response = requests.post(
                'https://auth.calendly.com/oauth/token', data=data,
                headers={
                    'Authorization': 'Basic ' + b64,
                    'content-type': 'application/x-www-form-urlencoded'})

            #raise UserError(response.json())
            if response.json() and response.json().get('access_token'):
                expires_in = response.json().get('expires_in')
                new_token_validity = datetime.now() + timedelta(seconds=expires_in)
                company_id.write({
                    'calendly_access_token': response.json().get('access_token'),
                    'calendly_refresh_token':  response.json().get('refresh_token'),
                    'calendly_generated_access_token': True,
                    'calendly_token_validity': new_token_validity,
                })
                return "Authentication Success. You Can Close this window"
            else:
                raise UserError(
                    _('Something went wrong during the token generation.'
                      'Maybe your Authorization Code is invalid'))
                #raise UserError(response.json().get('access_token'))
                
            #raise UserError(response)
            

            