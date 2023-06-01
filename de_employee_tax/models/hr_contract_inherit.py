# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class HrContractHistoryInherit(models.Model):
    _inherit = 'hr.contract'

    annual_salary = fields.Float(string='Annual Salary')
    other_income_including_interest = fields.Float(string='Other Income Including Interest')
    gross_income = fields.Float(string='Gross Income', compute='_compute_gross_income')
    deduction_description_ids = fields.One2many('deduction.description', 'contract_id', string='Deduction Description')
    total_deduction = fields.Float(string='Total Deductions', compute='_compute_total_deduction')
    extra_char = fields.Float(string='Total Deductions', compute='_compute_extra_char')
    taxable_amount = fields.Float(string='Taxable Amount', compute='_compute_taxable_amount')
    tax_payable = fields.Float(string='Tax Payable', compute='_compute_tax_payable')
    tax = fields.Char(string='Tax', compute='_compute_tax')
    monthly_deduction = fields.Boolean(string='Monthly Deduction')
    tds_deduction_per_month = fields.Float(string='TDS Deduction Per Month', compute='_compute_tds_deduction_per_month')
    extra_charges_ids = fields.One2many('extra.charges', 'contract_id')

    @api.depends('annual_salary', 'other_income_including_interest')
    def _compute_gross_income(self):
        self.gross_income = 0
        for rec in self:
            rec.gross_income = rec.annual_salary + rec.other_income_including_interest

    @api.depends('gross_income', 'total_deduction')
    def _compute_taxable_amount(self):
        self.taxable_amount = 0
        for record in self:
            record.taxable_amount = record.gross_income - record.total_deduction

    @api.depends('taxable_amount')
    def _compute_tax(self):
        self.tax = '0'
        for rec in self:
            tax_slab = self.env['tax.slabs'].search([])
            for slab in tax_slab:
                if slab.applied_from <= rec.taxable_amount <= slab.applied_to:
                    self.tax = slab.name
            # rec.tax_amount = total_tax

    @api.depends('deduction_description_ids')
    def _compute_total_deduction(self):
        total_amount = 0
        for record in self:
            for line in record.deduction_description_ids:
                total_amount += line.amount
            record.total_deduction = total_amount

    @api.depends('extra_charges_ids')
    def _compute_extra_char(self):
        total_amount = 0
        for record in self:
            for line in record.extra_charges_ids:
                total_amount += line.amount
            record.extra_char = total_amount

    @api.depends('taxable_amount')
    def _compute_tax_payable(self):
        self.tax_payable = 0
        for rec in self:
            rec.tax_payable = 0
            tax_slab = self.env['tax.slabs'].search([])
            for slab in tax_slab:
                if slab.applied_from <= rec.taxable_amount <= slab.applied_to:
                    percent = slab.tax_percent
                    rec.tax_payable = (percent / 100 * rec.taxable_amount) + rec.extra_char

    @api.depends('monthly_deduction', 'tax_payable')
    def _compute_tds_deduction_per_month(self):
        self.tds_deduction_per_month = 0
        for rec in self:
            rec.tds_deduction_per_month = 0
            if rec.monthly_deduction == True:
                rec.tds_deduction_per_month = rec.tax_payable / 12
