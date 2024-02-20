# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class OperationWizard(models.TransientModel):
    _name = 'sale.sub.op.wizard'
    _description = 'Subscription Operations Wizard'

    def run_process(self):
        pass