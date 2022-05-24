# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2019-today Dynexcel <www.dynexcel.com>

#
#################################################################################

from odoo import api, fields, models, _

class GatepassvouccherWizard(models.TransientModel):
    _name = "gatepass.voucher.wizard"
    _description = "Gatepass Voucher Wizard"

    start_date = fields.Date(string='From Date', required='1', help='select start date')
    end_date = fields.Date(string='To Date', required='1', help='select end date')

    def check_report(self):
        data = {}
        data['form'] = self.read(['start_date', 'end_date'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['start_date', 'end_date'])[0])
        return self.env.ref('de_account_voucher_report.open_gatepass_voucher_action').report_action(self, data=data, config=False)