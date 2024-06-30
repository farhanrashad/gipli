# -*- coding: utf-8 -*-

from odoo import api, fields, Command, models, _
from odoo.exceptions import UserError, AccessError

class AplOpsWizard(models.TransientModel):
    _name = 'xpl.ops.wizard'
    _description = 'Xpendless Ops Wizard'

    def run_process(self):
        pass