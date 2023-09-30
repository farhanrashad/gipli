# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HRLoanRjectWizard(models.TransientModel):
    _name = "hr.loan.reject.wizard"
    _description = 'Loan Reject Wizard'

    note = fields.Char(string='Reject Reason')

    def action_loan_reject(self):
        self.ensure_one()
        loan_id = self.env['hr.loan'].browse(self.env.context.get('active_id'))
        message_subject = "Loan Request Refused"
        message_body = "Loan request has been refused by." + self.env.user.name
        loan_id.message_post(body=message_body, subject=message_subject)
        loan_id.write({
            'state': 'refuse',
        })