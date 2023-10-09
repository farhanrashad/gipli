# -*- coding: utf-8 -*-

import requests
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class APLSendDataWizard(models.TransientModel):
    _name = "apl.send.data.wizard"
    _description = 'Search People Wizard'

    apl_instance_id = fields.Many2one('apl.instance')

    def action_process(self):
        active_model = self.env.context.get('active_model')
        raise UserError(active_model)