# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import json

class TicketCustomerPortal(CustomerPortal):
    @http.route('/xpl/logs', type='http', auth="user", website=True)
    def portal_xpendless_logs(self, **kw):
        # Sample logs data as JSON string
        logs = """
        {
            "logs": [
                {
                    "id": 1,
                    "message": "User logged in successfully",
                    "timestamp": "2023-01-01T12:00:00Z"
                },
                {
                    "id": 2,
                    "message": "User created a new record",
                    "timestamp": "2023-01-01T12:30:00Z"
                },
                {
                    "id": 3,
                    "message": "System error encountered",
                    "timestamp": "2023-01-01T13:00:00Z"
                },
                {
                    "id": 4,
                    "message": "User logged out",
                    "timestamp": "2023-01-01T13:30:00Z"
                }
            ]
        }
        """
        
        # Parse the JSON string into a Python dictionary
        log_data = json.loads(logs)
        
        # Prepare the values dictionary
        values = {
            'logs': log_data['logs']
        }
        
        # Render the template with the values
        return request.render("de_xpendless.portal_xpendless_logs", values)
