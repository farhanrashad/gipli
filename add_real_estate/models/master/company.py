# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    payment_journal_id = fields.Many2one(comodel_name="account.journal", string="Payment Default Journal", required=False)
    invoice_journal_id = fields.Many2one(comodel_name="account.journal", string="invoice Default Journal", required=False)
    tax_file_no = fields.Char(string='Tax File No')
    taxxx_id = fields.Char(string='Tax Id')
    name_arabic = fields.Char(string="Name Arabic", required=False, )





class CompanyData(models.Model):
    _name='real.company.data'
    name = fields.Many2one(comodel_name="res.company", string="Company", required=False)
    company_details = fields.Text('بيانات الشركه')

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            self.company_details=self.name.company_details