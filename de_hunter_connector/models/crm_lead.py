# -*- coding: utf-8 -*-

import requests
import json

from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError, ValidationError
import pprint

from urllib.parse import urlparse

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    def action_find_at_hunter(self):
        return {
            'name': _('Hunter'),
            'res_model': 'hunter.api.call.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'crm.lead',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    