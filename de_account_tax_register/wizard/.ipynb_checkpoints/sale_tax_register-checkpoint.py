# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2019-today Ascetic Business Solution <www.dynexcel.com>

#
#################################################################################

from odoo import api, fields, models, _

class InvoiceOutstanding(models.TransientModel):
    _name = "sale.tax.register.wizard"
    _description = "Sales Tax Register Wizard"

    start_date = fields.Date(string='From Date', required=True, help='select start date')
    end_date = fields.Date(string='To Date', required=True, help='select end date')
    target_move = fields.Selection([
        ('posted', "All Posted Entries"),
        ('all', "All Entries")], default='posted', )



    def check_report(self):
        data = {}
        data['form'] = self.read(['start_date', 'end_date','target_move'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['start_date', 'end_date','target_move'])[0])
        return self.env.ref('de_account_tax_register.open_sale_tax_register_action').report_action(self, data=data, config=False)


