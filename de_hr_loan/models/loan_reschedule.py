# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import models, fields, api, _
from odoo.tools.misc import frozendict

READONLY_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'confirm', 'validate1', 'validate' ,'done','refuse'}
}

class LoanReschedule(models.Model):
    _name = "hr.loan.reschedule"
    _description = "Loan Reschedule"

    name = fields.Char('Reference', required=True, index='trigram', copy=False, default='New')
    loan_id = fields.Many2one('hr.loan', string='Loan')
    employee_id = fields.Many2one(related='loan_id.employee_id')
    loan_type_id = fields.Many2one(related='loan_id.loan_type_id')
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True, help="Loan Request Date",states=READONLY_FIELD_STATES,)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('verify', 'Verified'),
        ('confirm', 'To Approve'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved'),
        ('done', 'Done'),
        ('refuse', 'Refused'),
        ], string='Status', default='draft', store=True, tracking=True, copy=False, readonly=False,
        help="The status is set to 'To Submit', when a time off request is created." +
        "\nThe status is 'To Approve', when request is confirmed by user." +
        "\nThe status is 'Refused', when request is refused by manager." +
        "\nThe status is 'Approved', when request is approved by manager.")

    # ------------------------------------------------
    # ----------- Operations -------------------------
    # ------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'hr.loan.reschedule') or _('New')
        res = super(LoanReschedule, self).create(vals_list)
        return res
        
    def unlink(self):
        for loan in self:
            if loan.state not in ('draft', 'cancel'):
                raise UserError(
                    'You cannot delete a loan which is not in draft or cancelled state')
        return super(HrLoan, self).unlink()
