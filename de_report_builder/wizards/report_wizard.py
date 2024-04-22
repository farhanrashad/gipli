# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError

class ReportWizard(models.TransientModel):
    _name = 'rc.report.wizard'
    _description = 'Custom Report Wizard'

    def generate_report(self):
        data = {
            'date_start': False, 
            'date_stop': False, 
            'config_ids': False,
        }
        return self.env.ref('de_report_builder.action_custom_report').report_action([], data=data)