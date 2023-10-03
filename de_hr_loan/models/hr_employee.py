# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    #def create_loan_reconcile_entry(self, loan_id, loan_line_id, account_move_id):
    #    reconcile_record = self.env['hr.loan.reconcile'].create({
    #        'loan_id': loan_id,
    #        'loan_line_id': loan_line_id,
    #        'account_move_id': account_move_id,
    #    })
    #    return reconcile_record

    def compute_loan_from_payslip(self, record_id, model):
        record = record_id
        payslip_id = self.env[model].browse(record)
        amount = sum(payslip_id.x_loan_lines.mapped('amount'))
        return amount

    

