# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class hr_salary_rule(models.Model):
    _inherit = 'hr.salary.rule'
    
    salary_adjustment = fields.Boolean(string='Salary Adjustment')
    computation_report = fields.Boolean(string='Tax Computation')
    report_label = fields.Char(string='Heading')
    computation_sequence = fields.Integer(string='Sequence')
    include_total = fields.Boolean(string='Include In Total')
    reconcile_deduction = fields.Boolean(string='Reconcile Deduction')
    reconcile_compansation = fields.Boolean(string='Reconcile Compansation')
    reconcilation_details = fields.Boolean(string="Reconcilation Details")
    pfund_amount = fields.Boolean(string='Pfund Exceeding Limit')
    
    detail_report = fields.Boolean(string='Detail Report')
    detail_label = fields.Char(string='Heading')
    detail_sequence = fields.Integer(string='Sequence')
    detail_deduction = fields.Boolean(string='Deduction')
    detail_compansation = fields.Boolean(string='Compansation')

    