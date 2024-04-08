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

class CalendlyCallbackController(http.Controller):

    @http.route('/calendly/oauth', type='http', auth='public', website=True)
    def handle_calendly_callback(self, **kw):

        company_id = request.env.user.company_id or http.request.env['res.users'].sudo().browse(
            user_id).company_id
        user_id = request.uid
        client_id = company_id.calendly_client_id
        client_secret = company_id.calendly_client_secret
        redirect_uri = request.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/calendly/oauth'

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
                'https://auth.calendly.com/oauth/token', data=data,
                headers={
                    'Authorization': 'Basic ' + cient_id_secret,
                    'content-type': 'application/x-www-form-urlencoded'})

            if response.json() and response.json().get('access_token'):
                company_id.write(self._prepare_calendly_token_values(response))
                
        return request.redirect(request.httprequest.referrer or '/')

    def _prepare_calendly_token_values(self, response):
        expires_in = response.json().get('expires_in')
        token_validity = datetime.now() + timedelta(seconds=expires_in)
        return {
            'calendly_access_token': response.json().get('access_token'),
            'calendly_refresh_token':response.json().get('refresh_token'),
            'calendly_token_validity':token_validity,
            'calendly_generated_access_token': True,
        }

        
    @http.route('/calendly/invitee/created', type='json', auth='none', methods=['POST'])
    def create_invitee_created(self, **kw):
        if kw.get('payload'):
            _logger.info(f"Calendly Event Data: {payload}")
            # Pass the payload to the model method for processing
            payload = json.loads(kw['payload'])
            self.env['calendly.webhook'].handle_webhook_event(payload)
        return {'status': 'success'}

            