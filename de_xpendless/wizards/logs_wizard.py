# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _
from odoo.exceptions import UserError, AccessError

class AplLogsWizard(models.TransientModel):
    _name = 'xpl.logs.wizard'
    _description = 'Xpendless Logs Wizard'

    def run_process(self):
        # Define the parameters to be sent
        param1 = 'value1'
        param2 = 'value2'
        
        # Construct the URL
        url = '/xpl/logs?param1={}&param2={}'.format(param1, param2)
        
        # Return an action to redirect to the URL
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',  # Open in a new tab/window
        }

    