# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import requests
import logging

_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError

class CalendlyCallbackController(http.Controller):

    @http.route('/calendly/callback', type='http', auth='public', website=True)
    def handle_calendly_callback(self, **kwargs):
        authorization_code = kwargs.get('code')

        # Fetch OAuth credentials from Calendly instance
        calendly_instance = request.env['cal.instance'].sudo().search([], limit=1)
        if not calendly_instance:
            return 'Calendly instance not found'

        client_id = calendly_instance.client_id
        client_secret = calendly_instance.client_secret
        redirect_uri = calendly_instance.url + '/calendly/callback'

        # Exchange authorization code for access token
        token_url = 'https://auth.calendly.com/oauth/token'
        token_data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
        }

        
        response = requests.post(token_url, data=token_data)
        raise UserError(response)
        if response.status_code == 200:
            access_token = response.json().get('access_token')

            # Update the state and store the access token in Calendly instance
            calendly_instance.write({'state': 'verified', 'access_token': access_token})

            # Update the front-end using JavaScript to indicate successful connection
            return """
            <html>
                <body>
                    <script>
                        alert('Calendly connection verified!');
                        window.location.href = '/web#id={}&view_type=form&model=cal.instance';
                    </script>
                </body>
            </html>
            """.format(calendly_instance.id)
        else:
            error_message = response.json().get('error_description', 'Unknown error')
            _logger.error('Error obtaining access token from Calendly: %s', error_message)
            return 'Error occurred while obtaining access token: {}'.format(error_message)
