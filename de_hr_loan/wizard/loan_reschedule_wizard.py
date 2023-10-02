# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HRLoanResheduleWizard(models.TransientModel):
    _name = "hr.loan.reschedule.wizard"
    _description = 'Loan Reschedule Wizard'

    note = fields.Char(string='Reason', required=True)
    interval_loan = fields.Integer(string='Interval', required=True)

    def action_loan_reschedule(self):
        self.ensure_one()
        loan_id = self.env['hr.loan'].browse(self.env.context.get('active_id'))
        message_subject = "Loan Reschedule Request created by " + self.env.user.name
        message_body = self.note
        loan_id.message_post(body=message_body, subject=message_subject)
        loan_reschedule_id = self.env['hr.loan.reschedule'].create({
            'loan_id': loan_id.id,
            'date': fields.Date.today(),
            'interval_loan': self.interval_loan,
            'note': self.note,
        })
        loan_reschedule_id.message_post(body=message_body, subject=message_subject)
        loan_reschedule_id.action_confirm()