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
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Loan Reschedule"

    name = fields.Char('Reference', required=True, index='trigram', copy=False, default='New')
    loan_id = fields.Many2one('hr.loan', string='Loan')
    employee_id = fields.Many2one(related='loan_id.employee_id')
    loan_type_id = fields.Many2one(related='loan_id.loan_type_id')
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True, help="Loan Request Date",states=READONLY_FIELD_STATES,)
    interval_loan = fields.Integer(string='Interval', required=True)

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

    # ------------------------------------------------
    # -------------- Action Buttons ------------------
    # ------------------------------------------------
    def action_draft(self):
        for record in self:
            record.write({
                'state':'draft'
            })
    def action_confirm(self):
        #if self.filtered(lambda loan: loan.state != 'draft' or loan.state != 'verify'):
        #    raise UserError(_('Request must be in Draft state ("To Submit") in order to confirm it.')) 
        self.write({'state': 'confirm'})
        self.activity_update()
        return True
        
    def action_refuse(self):
        template = self.env.ref('de_hr_loan.loan_reject_email_temp')
        template.send_mail(self.id, force_send=True)
        return self.write({'state': 'refuse'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_approve(self):
        for loan in self:            
            template = self.env.ref('de_hr_loan.loan_approval_mail')
            template.send_mail(self.id, force_send=True)
            self.write({'state': 'validate'})
            self.message_post(
                body=_(
                    'Your Encashment Request for %(leave_type)s on %(date)s has been accepted',
                    leave_type=self.loan_type_id.name,
                    date=self.date
                ),
                partner_ids=self.employee_id.user_id.partner_id.ids)
            self.activity_update()

    def _get_responsible_for_approval(self):
        self.ensure_one()
        responsible = self.env.user
        return responsible
        
    def activity_update(self):
        to_clean, to_do = self.env['hr.loan.reschedule'], self.env['hr.loan.reschedule']
        for loan in self:
            note = _(
                'New %(loan_type)s Request created by %(user)s',
                loan_type=loan.loan_type_id.name,
                user=loan.create_uid.name,
            )
            if loan.state == 'draft':
                to_clean |= loan
            elif loan.state == 'confirm':
                loan.activity_schedule(
                    'de_hr_loan.mail_act_loan_confirm',
                    note=note,
                    user_id=loan.sudo()._get_responsible_for_approval().id or self.env.user.id)
            elif loan.state == 'validate1':
                loan.activity_feedback(['de_hr_loan.mail_act_loan_confirm'])
                loan.activity_schedule(
                    'de_hr_loan.mail_act_loan_second_approval',
                    note=note,
                    user_id=loan.sudo()._get_responsible_for_approval().id or self.env.user.id)
            elif loan.state == 'validate':
                to_do |= loan
            elif loan.state == 'refuse':
                to_clean |= loan
        if to_clean:
            to_clean.activity_unlink(['de_hr_loan.mail_act_loan_confirm', 'de_hr_loan.mail_act_loan_second_approval'])
        if to_do:
            to_do.activity_feedback(['de_hr_loan.mail_act_loan_approval', 'de_hr_loan.mail_act_loan_second_approval'])
