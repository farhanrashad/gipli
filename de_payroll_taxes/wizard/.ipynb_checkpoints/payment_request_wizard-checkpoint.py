# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

class PaymentRequestWizard(models.TransientModel):
    _name = 'payment.request.wizard'
    _description='Payment Request Wizard'
    
    company_ids = fields.Many2many('res.company', string='Company')
    date = fields.Date(string='Date', required=True)

    def check_report(self):
        data = {}
        data['form'] = self.read(['company_ids','date'])[0]
        return self._print_report(data)

    
    def _print_report(self, data):
        data['form'].update(self.read(['company_ids','date'])[0])
        return self.env.ref('de_payroll_taxes.open_payment_request_action').report_action(self, data=data, config=False)
  
    
