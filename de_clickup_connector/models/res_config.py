# -*- coding: utf-8 -*-
from odoo import models, fields, api, _



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    
    def test_credentials(self):
        pass