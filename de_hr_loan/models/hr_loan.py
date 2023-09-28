# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta, time
from pytz import timezone, UTC
from odoo.tools import date_utils
from odoo.addons.base.models.res_partner import _tz_get
from dateutil.relativedelta import relativedelta

class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Loan Request"
    _order = 'id desc'

    @api.model
    def _default_employee_id(self):
        return self.env.user.employee_id

    @api.model
    def _default_journal_id(self):
        default_company_id = self.default_get(['company_id']).get('company_id')
        journal = self.env['account.journal'].search([('type', '=', 'purchase'), ('company_id', '=', default_company_id)], limit=1)
        return journal.id

    def _get_employee_id_domain(self):
        res = [('id', '=', 0)] # Nothing accepted by domain, by default
        if self.user_has_groups('de_hr_loan.group_loan_user') or self.user_has_groups('account.group_account_user'):
            res = "['|', ('company_id', '=', False), ('company_id', '=', company_id)]"  # Then, domain accepts everything
        elif self.user_has_groups('de_hr_loan.group_loan_manager') and self.env.user.employee_ids:
            user = self.env.user
            employee = self.env.user.employee_id
            res = [
                '|', '|', '|',
                ('department_id.manager_id', '=', employee.id),
                ('parent_id', '=', employee.id),
                ('id', '=', employee.id),
                '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id),
            ]
        elif self.env.user.employee_id:
            employee = self.env.user.employee_id
            res = [('id', '=', employee.id), '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id)]
        return res
        
    @api.model
    def default_get(self, field_list):
        result = super(HrLoan, self).default_get(field_list)
        if result.get('user_id'):
            ts_user_id = result['user_id']
        else:
            ts_user_id = self.env.context.get('user_id', self.env.user.id)
        result['employee_id'] = self.env['hr.employee'].search([('user_id', '=', ts_user_id)], limit=1).id
        return result

    def _compute_loan_amount(self):
        total_paid = 0.0
        for loan in self:
            for line in loan.loan_lines:
                if line.paid:
                    total_paid += line.amount
            balance_amount = loan.loan_amount - total_paid
            loan.total_amount = loan.loan_amount
            loan.balance_amount = balance_amount
            loan.total_paid_amount = total_paid

    READONLY_STATES = {
        'confirm': [('readonly', True)],
        'refuse': [('readonly', True)],
        'validate': [('readonly', True)],
        'validate1': [('readonly', True)],
        'post': [('readonly', True)],
        'done': [('readonly', True)],
    }
    
    name = fields.Char('Loan Reference', required=True, index='trigram', copy=False, default='New')
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True, help="Date")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, readonly=False, tracking=True,
                                  states=READONLY_STATES, default=_default_employee_id, check_company=True, 
                                  domain=lambda self: self.env['hr.loan']._get_employee_id_domain())
    
    loan_type_id = fields.Many2one("hr.loan.type", store=True, string="Loan Type", 
                                   required=True, readonly=False, states=READONLY_STATES,tracking=True)
    company_id = fields.Many2one(related='employee_id.company_id', readonly=True, store=True)
    currency_id = fields.Many2one('res.currency', string='Currency',                               
                                  compute='_compute_currency_id', store=True, readonly=True)
    loan_amount = fields.Float(string="Loan Amount", required=True, help="Loan amount",states=READONLY_STATES,)
    installment = fields.Integer(string="No Of Installments", default=1, help="Number of installments", states=READONLY_STATES,)
    date_start = fields.Date(string="Loan Start Date", required=True, default=fields.Date.today(), 
                               help="Date of Start", states=READONLY_STATES,)
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_from_employee_id', store=True)
    job_id = fields.Many2one('hr.job', string='Job', compute='_compute_from_employee_id')

    account_move_id = fields.Many2one('account.move', string='Journal Entry', ondelete='restrict', copy=False, readonly=True)
    accounting_date = fields.Date(
        string='Accounting Date',
        compute='_compute_accounting_date',
        states={'validate': [('readonly', False)], 'post': [('readonly', False)]},
        store=True
    )
    journal_id = fields.Many2one('account.journal', string='Accounting Journal', check_company=True, domain="[('type', '=', 'purchase'), ('company_id', '=', company_id)]",
        states={'validate': [('readonly', False)], 'post': [('readonly', False)]},
        default=_default_journal_id, help="The journal used when the request is done.")
    address_id = fields.Many2one('res.partner', compute='_compute_from_employee_id', store=True, readonly=False, copy=True, string="Employee Home Address", check_company=True)

    loan_lines = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", index=True, states=READONLY_STATES,)
    
    
    total_amount = fields.Float(string="Total Amount", store=True, readonly=True, compute='_compute_loan_amount',
                                help="Total loan amount")
    balance_amount = fields.Float(string="Balance Amount", store=True, compute='_compute_loan_amount',
                                  help="Balance amount")
    total_paid_amount = fields.Float(string="Total Paid Amount", store=True, compute='_compute_loan_amount',
                                     help="Total paid amount")
    description = fields.Text(string='Description', states=READONLY_STATES, readonly=False)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('verify', 'Verified'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved'),
        ('post', 'Posted'),
        ('done', 'Done'),
        ], string='Status', default='draft',compute='_compute_state', store=True, tracking=True, copy=False, readonly=False,
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
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.loan') or _('New')
        res = super(HrLoan, self).create(vals_list)
        return res
        
    def unlink(self):
        for loan in self:
            if loan.state not in ('draft', 'cancel'):
                raise UserError(
                    'You cannot delete a loan which is not in draft or cancelled state')
        return super(HrLoan, self).unlink()

    # ------------------------------------------------
    # -------------- Methods -------------------------
    # ------------------------------------------------
    def _compute_state(self):
        for leave in self:
            if leave.account_move_id.payment_state in ('paid','in_payment'):
                leave.state = 'done'
            elif not leave.state:
                leave.state = 'draft'

    @api.depends('company_id.currency_id')
    def _compute_currency_id(self):
        for record in self:
            if not record.currency_id or record.state not in {'post', 'done', 'refuse'}:
                record.currency_id = record.company_id.currency_id
                
    def compute_installment(self):
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        for loan in self:
            loan.loan_lines.unlink()
            date_start = datetime.strptime(str(loan.date_start), '%Y-%m-%d')
            amount = loan.loan_amount / loan.installment
            for i in range(1, loan.installment + 1):
                self.env['hr.loan.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id})
                date_start = date_start + relativedelta(months=1)
            loan._compute_loan_amount()
            loan.write({
                'state': 'verify',
            })
        return True

    @api.depends('account_move_id.date')
    def _compute_accounting_date(self):
        for record in self:
            record.accounting_date = record.account_move_id.date

    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for record in self:
            record.address_id = record.employee_id.sudo().address_home_id.id
            record.department_id = record.employee_id.sudo().department_id
            record.job_id = record.employee_id.sudo().job_id

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

    def action_submit(self):
        self.write({'state': 'waiting_approval_1'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_approve(self):
        for loan in self:
            if not loan.loan_lines:
                raise ValidationError(_("Please Compute installment"))
            
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

    def action_request_move_create(self):
        if any(request.state != 'validate' for request in self):
            raise UserError(_("You can only generate accounting entry for approved request(s)."))

        if any(not request.journal_id for request in self):
            raise UserError(_("Specify journal to generate accounting entries."))

        if not self.employee_id.sudo().address_home_id:
            raise UserError(_("The private address of the employee is required to post the accounting document. Please add it on the employee form."))

        # Create a vendor bill
        account_move_id = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.employee_id.sudo().address_home_id.id,
            'journal_id': self.journal_id.id,
            'invoice_date': fields.Date.today(),
            'date': self.accounting_date or fields.Date.context_today(self),
            'ref': self.name,
            'currency_id': self.currency_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.loan_type_id.product_id.id,
                    'quantity': 1,
                    'price_unit': self.loan_amount,
                    'name': self.description or self.loan_type_id.product_id.display_name,
                })
            ],
        })
        
        self.write({
            'state': 'post',
            'account_move_id': account_move_id.id
        })

        self.activity_update()
        
    def _get_responsible_for_approval(self):
        self.ensure_one()
        responsible = self.env.user
        return responsible
        
    def activity_update(self):
        to_clean, to_do = self.env['hr.loan'], self.env['hr.loan']
        for loan in self:
            note = _(
                'New %(loan_type)s Encashment Request created by %(user)s',
                loan_type=loan.loan_type_id.name,
                user=loan.create_uid.name,
            )
            if loan.state == 'draft':
                to_clean |= loan
            elif loan.state == 'confirm':
                loan.activity_schedule(
                    'de_hr_loan.mail_act_loan_approval',
                    note=note,
                    user_id=loan.sudo()._get_responsible_for_approval().id or self.env.user.id)
            elif loan.state == 'validate1':
                loan.activity_feedback(['de_hr_loan.mail_act_loan_approval'])
                loan.activity_schedule(
                    'de_hr_loan.mail_act_loan_second_approval',
                    note=note,
                    user_id=loan.sudo()._get_responsible_for_approval().id or self.env.user.id)
            elif loan.state == 'validate':
                to_do |= loan
            elif loan.state == 'refuse':
                to_clean |= loan
        if to_clean:
            to_clean.activity_unlink(['de_hr_loan.mail_act_loan_approval', 'de_hr_loan.mail_act_loan_second_approval'])
        if to_do:
            to_do.activity_feedback(['de_hr_loan.mail_act_loan_approval', 'de_hr_loan.mail_act_loan_second_approval'])

    def action_open_account_move(self):
        self.ensure_one()
        return {
            'name': self.account_move_id.name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [[False, "form"]],
            'res_model': 'account.move',
            'res_id': self.account_move_id.id,
        }
class InstallmentLine(models.Model):
    _name = "hr.loan.line"
    _description = "Installment Line"

    date = fields.Date(string="Payment Date", required=True, help="Date of the payment")
    employee_id = fields.Many2one('hr.employee', string="Employee", help="Employee")
    amount = fields.Float(string="Amount", required=True, help="Amount")
    paid = fields.Boolean(string="Paid", help="Paid")
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.", help="Loan")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.", help="Payslip")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _compute_employee_loans(self):
        """This compute the loan amount and total loans count of an employee.
            """
        self.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', self.id)])

    loan_count = fields.Integer(string="Loan Count", compute='_compute_employee_loans')
