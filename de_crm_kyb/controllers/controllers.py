from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class WebhookController(http.Controller):

    @http.route('/webhook/company', type='json', auth='public', csrf=False, methods=['POST'])
    def handle_webhook(self, **kwargs):
        try:
            # Extract JSON data from request
            data = request.get_json_data()
            
            # Debug logging
            _logger.info(f"Received webhook payload: {payload}")

            # Process payload further as per your application logic
            # Example: Create a record in a model
            request.env['your.model'].sudo().create(payload)

            # Return a response if required
            return {'status': 'ok'}
        except Exception as e:
            # Debug logging
            _logger.error(f"Error processing webhook: {e}")
            
            # Handle exceptions gracefully
            return {'error': str(e)}, 500  # Return HTTP 500 Internal Server Error with error message
