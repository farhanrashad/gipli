from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class WebhookController(http.Controller):

    @http.route('/webhook/company', type='json', auth='public', csrf=False, methods=['POST'])
    def handle_webhook(self, **kwargs):
        data = request.get_json_data()
        lead = request.env['crm.lead'].sudo().create_or_update_opportunity(data)

        if lead:
            # Ensure that the lead has been created or updated
            lead.ensure_one()  # Ensures only one record is returned
            return {'lead_id': lead.id}
        else:
            _logger.error("Lead creation or update failed.")
            return {'error': 'Lead creation or update failed'}
   