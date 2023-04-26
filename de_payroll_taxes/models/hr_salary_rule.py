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

    deduction_summary_seq = fields.Integer(string='Deduction Sequence') 
    deduction_summary_label = fields.Char(string='Deduction Label') 
    compansation_summary_seq = fields.Integer(string='Compansation Sequence') 
    compansation_summary_label = fields.Char(string='Compansation Label')
    detail_reconcile_seq = fields.Integer(string='Sequence')
    detail_reconcile_label = fields.Char(string='Detail Label')    
    
    ora_account_service = fields.Boolean(string='Payment Request')
    ora_account_label = fields.Char(string='Label')
    ora_payment_type = fields.Char(string='Payment Type')
    ora_account_code = fields.Char(string='Account Code')
    ora_split_location = fields.Boolean(string='Location Wise')
    ora_account_gl_code = fields.Char(string='ORA GL Code')
    ora_rule_id = fields.Many2one('hr.salary.rule', string='Parent Rule')

    ora_extra_to_ded = fields.Boolean(string='Rule to Deduct')
    ora_extra_from_ded = fields.Boolean(string='Rule From Deduct')