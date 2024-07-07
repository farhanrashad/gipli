# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import UserError, AccessError

import json

class TicketCustomerPortal(CustomerPortal):
    @http.route('/xpl/logs', type='http', auth="user", website=True)
    def portal_xpendless_logs(self, **kw):
        # Sample logs data as JSON string
        
        instance_id = request.env.company._get_instance()
        json_data = instance_id._get_api_data('webhook/logs', api_data=None)
        json_formatted_str = json.dumps(json_data, indent=4)  # Convert dictionary to JSON string with indentation
        
        if not json_data.get('status'):
            raise UserError('Failed to fetch data')
        
        # Extract the relevant fields from the first log entry
        log_entry = json_data['data'][0]
        filtered_data = {
            "webhookLogId": log_entry.get("webhookLogId"),
            "eventName": log_entry.get("eventName"),
            "status": log_entry.get("status"),
            "type": log_entry.get("type"),
            "endpoint": log_entry.get("endpoint"),
            "maxRetries": log_entry.get("maxRetries"),
            "retries": log_entry.get("retries"),
            "isInfinityRetries": log_entry.get("isInfinityRetries"),
            "retryInterval": log_entry.get("retryInterval"),
            "createdAt": log_entry.get("createdAt"),
            "updatedAt": log_entry.get("updatedAt"),
        }

        
       # Prepare the values dictionary
        values = {
            'logs': [
                {
                    'webhookLogId': filtered_data["webhookLogId"],
                    'eventName': filtered_data['eventName'],
                    'status': filtered_data['status'],
                    'type': filtered_data['type'],
                    'endpoint': filtered_data['endpoint'],
                    'maxRetries': filtered_data['maxRetries'],
                    'retries': filtered_data['retries'],
                    'isInfinityRetries': filtered_data['isInfinityRetries'],
                    'retryInterval': filtered_data['retryInterval'],
                    'createdAt': filtered_data['createdAt'],
                    'updatedAt': filtered_data['updatedAt'],
                }
            ]
        }
        
        # Prepare the values dictionary
        #values = {
        #    'logs': log_data['logs']
        #}
        
        # Render the template with the values
        return request.render("de_xpendless.portal_xpendless_logs", values)
