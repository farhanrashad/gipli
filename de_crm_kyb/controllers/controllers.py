from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class WebhookController(http.Controller):

    @http.route('/webhook/company', type='json', auth='public', csrf=False, methods=['POST'])
    def handle_webhook(self, **kwargs):
        data = request.get_json_data()
        #lead_id = request.env['crm.lead'].sudo().create_or_update_opportunity(data)

        #result = data.get('id')
        return data

   