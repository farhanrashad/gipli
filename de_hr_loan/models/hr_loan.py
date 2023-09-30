# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta, time
from pytz import timezone, UTC
from odoo.tools import date_utils
from odoo.addons.base.models.res_partner import _tz_get
from dateutil.relativedelta import relativedelta

from odoo.tools import safe_eval


READONLY_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'confirm', 'validate1', 'validate' ,'post','paid','partial','close','refuse'}
}

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
    
    name = fields.Char('Loan Reference', required=True, index='trigram', copy=False, default='New')
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True, help="Loan Request Date",states=READONLY_FIELD_STATES,)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, readonly=False, tracking=True,
                                  default=_default_employee_id, check_company=True, states=READONLY_FIELD_STATES,
                                  domain=lambda self: self.env['hr.loan']._get_employee_id_domain())
    
    loan_type_id = fields.Many2one("hr.loan.type", store=True, string="Loan Type", states=READONLY_FIELD_STATES,
                                   required=True, readonly=False, tracking=True)
    company_id = fields.Many2one(related='employee_id.company_id', readonly=True, store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', states=READONLY_FIELD_STATES,                      
                                  compute='_compute_currency_id', store=True, readonly=True)

    interval_loan_mode = fields.Char(string='Interval Mode', compute='_compute_from_loan_type')
    interval_loan = fields.Integer(string="Loan Interval", default=1, store=True, required=True, readonly=False,
                                   compute='_compute_from_loan_type',
                                 help="Number of intervals to disburse loan", )
    repayment_mode = fields.Char(string='Repayment Mode', compute='_compute_from_loan_type')
    date_start = fields.Date(string="Loan Start Date", required=True, store=True, readonly=False,
                             compute='_compute_date_start',states=READONLY_FIELD_STATES,
                               help="Date of Start")
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_from_employee_id')
    job_id = fields.Many2one('hr.job', string='Job', compute='_compute_from_employee_id')

    # Amount fields
    amount = fields.Monetary(string="Loan Amount", required=True, help="Loan amount",states=READONLY_FIELD_STATES,)
    
    amount_paid = fields.Monetary(string="Paid Amount", store=True, readonly=True, compute='_compute_loan_amount',
                                help="Total Paid Amount for loan")
    amount_disbursed = fields.Monetary(string="Disbursed", store=True, compute='_compute_loan_amount',
                                  help="Total Amount recieved from Employee")
    amount_balance = fields.Monetary(string="Balance", store=True, compute='_compute_loan_amount',
                                     help="Total Remaining amount")

    # Accounting Fields
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

    loan_lines = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", index=True, states=READONLY_FIELD_STATES,)
    
    
    
    description = fields.Text(string='Description', readonly=False, states=READONLY_FIELD_STATES,)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('verify', 'Verified'),
        ('confirm', 'To Approve'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved'),
        ('post', 'Posted'),
        ('paid', 'Paid'),
        ('partial', 'Partially Reconciled'),
        ('close', 'Reconciled'),
        ('refuse', 'Refused'),
        ], string='Status', default='draft',compute='_compute_state', store=True, tracking=True, copy=False, readonly=False,
        help="The status is set to 'To Submit', when a time off request is created." +
        "\nThe status is 'To Approve', when request is confirmed by user." +
        "\nThe status is 'Refused', when request is refused by manager." +
        "\nThe status is 'Approved', when request is approved by manager.")


    loan_document_ids = fields.One2many('hr.loan.document', 'loan_id', string='Documents', states=READONLY_FIELD_STATES,)

    # ------------------------------------------------
    # ----------- Operations -------------------------
    # ------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            category = 'loan_type_id' in vals and self.env['hr.loan.type'].browse(vals['loan_type_id'])
            if category and category.automated_sequence:
                vals['name'] = category.sequence_id.next_by_id()
        return super().create(vals_list)
        
    def unlink(self):
        for loan in self:
            if loan.state not in ('draft', 'cancel'):
                raise UserError(
                    'You cannot delete a loan which is not in draft or cancelled state')
        return super(HrLoan, self).unlink()

    # ------------------------------------------------
    # -------------- Methods -------------------------
    # ------------------------------------------------
    @api.depends('account_move_id','account_move_id.payment_state',
                 'loan_lines','loan_lines.amount_paid')
    def _compute_loan_amount(self):
        total_paid = 0.0
        for loan in self:
            if loan.account_move_id.payment_state in ('paid','in_payment'):
                loan.amount_paid = loan.account_move_id.amount_total_signed
            else:
                loan.amount_paid = 0 
            loan.amount_disbursed = sum(loan.loan_lines.mapped('amount_paid'))
            loan.amount_balance = loan.amount - sum(loan.loan_lines.mapped('amount_paid'))
            
    @api.depends('account_move_id','account_move_id.payment_state','loan_lines','loan_lines.state')
    def _compute_state(self):
        for loan in self:
            if all(loan_line.state == 'close' for loan_line in loan.loan_lines):
                loan.state = 'close'
            elif any(loan_line.state == 'close' for loan_line in loan.loan_lines):
                loan.state = 'partial'
            else:
                if loan.account_move_id:
                    if loan.account_move_id.payment_state in ('paid','in_payment'):
                        loan.state = 'paid'
                elif not loan.state:
                    loan.state = 'draft'

    @api.depends('company_id.currency_id')
    def _compute_currency_id(self):
        for record in self:
            if not record.currency_id or record.state not in {'post', 'done', 'refuse'}:
                record.currency_id = record.company_id.currency_id

    @api.depends('loan_type_id','date')
    def _compute_date_start(self):
        for loan in self:
            loan.date_start = datetime.strptime(str(loan.date), '%Y-%m-%d') + relativedelta(months=1)
        
    @api.depends('loan_type_id')
    def _compute_from_loan_type(self):
        for loan in self:
            loan.interval_loan_mode = loan.loan_type_id.interval_loan_mode
            if loan.interval_loan <= 0:
                loan.interval_loan = loan.loan_type_id.interval_loan
            loan.repayment_mode = loan.loan_type_id.repayment_mode
                
    
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

    @api.onchange('loan_type_id')
    def generate_loan_documents(self):
        if self.loan_type_id:
            document_ids = self.env['hr.loan.type.document'].search([('loan_type_id','=',self.loan_type_id.id)])
            for doc in document_ids:
                vals = {
                    'name': doc.name,
                    'doc_desc': doc.name,
                    'is_mandatory': doc.is_mandatory,
                    'loan_id': self.id,
                }
                self.env['hr.loan.document'].create(vals)
            
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
        for loan in self:
            if not len(loan.loan_lines) or loan.amount <= 0:
                loan.action_compute_intervals()
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

    def action_compute_intervals(self):
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        for loan in self:
            if loan.amount <= 0:
                raise UserError(_('Loan amount must be greater than 0 in order to process it.'))
            
            if loan.interval_loan <= 0:
                raise UserError(_('Interval must be greater than 0 in order to process it.'))

            if loan.loan_type_id.interval_loan_mode == 'max':
                if loan.interval_loan > loan.loan_type_id.interval_loan:
                    raise UserError("Maximum allowed internal is %s" % loan.loan_type_id.interval_loan)

            contract_id = self.env['hr.contract'].search([('employee_id','=',loan.employee_id.id)],limit=1)
            amount_wage = contract_id[eval("'" + loan.loan_type_id.calculation_field_id.name + "'")] * (loan.loan_type_id.amount_per / 100)
            
            if loan.loan_type_id.calculation_type == 'fix':
                if loan.amount > loan.loan_type_id.fixed_amount:
                    raise UserError("Maximum allowed amount is %s for this loan type" % loan.loan_type_id.fixed_amount)
            elif loan.loan_type_id.calculation_type == 'percent':
                if loan.amount > amount_wage:
                    raise UserError("Your maximum amount limit for a %s is %s %s" % (loan.loan_type_id.name, amount_wage, loan.currency_id.name))
            
            loan.loan_lines.unlink()
            date_start = datetime.strptime(str(loan.date_start), '%Y-%m-%d')
            amount = loan.amount / loan.interval_loan
            for i in range(1, loan.interval_loan + 1):
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
                    'price_unit': self.amount,
                    'name': self.description or self.loan_type_id.product_id.display_name,
                })
            ],
        })
        self._create_credit_memo()
        self.write({
            'state': 'post',
            'account_move_id': account_move_id.id
        })

        self.activity_update()
        
    def _create_credit_memo(self):
        if self.loan_type_id.repayment_mode == 'credit_memo' and self.loan_type_id.prepayment_credit_memo:
            for line in self.loan_lines:
                # Create credit memo
                account_move_id = self.env['account.move'].create({
                    'move_type': 'in_refund',
                    'partner_id': self.employee_id.sudo().address_home_id.id,
                    'journal_id': self.journal_id.id,
                    'invoice_date': fields.Date.today(),
                    'invoice_date_due': line.date,
                    'date': line.date,
                    'ref': line.loan_id.name + '/' + line.date.strftime("%b") + '/' + line.date.strftime("%Y"),
                    'currency_id': self.currency_id.id,
                    'invoice_line_ids': [
                        (0, 0, {
                            'product_id': self.loan_type_id.product_id.id,
                            'quantity': 1,
                            'price_unit': line.amount,
                            'name': self.loan_type_id.product_id.display_name,
                        })
                    ],
                })
                #account_move_id.action_post()
                line.write({
                    'state': 'pending',
                    'res_id': account_move_id.id,
                    'model': 'account.move',
                    'res_name': account_move_id.name,
                    'account_move_id': account_move_id.id,
                })
        
    def _get_responsible_for_approval(self):
        self.ensure_one()
        responsible = self.env.user
        return responsible
        
    def activity_update(self):
        to_clean, to_do = self.env['hr.loan'], self.env['hr.loan']
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
class HRLoanLine(models.Model):
    _name = "hr.loan.line"
    _description = "Installment Line"

    date = fields.Date(string="Due On", required=True, help="Due Date")
    employee_id = fields.Many2one('hr.employee', string="Employee", help="Employee")
    amount = fields.Float(string="Amount", required=True, help="Amount")
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.", help="Loan")
    state = fields.Selection([
        ('draft', 'Open'),
        ('pending', 'Pending'),
        ('close', 'Close'),
        ], string='Status', default='draft',store=True, tracking=True, copy=False, readonly=False,
            compute='_compute_state',
        help="The status is set to 'draft', when an installment is created." +
        "\nThe status is 'pending', when subsequent disbursement document is created." +
        "\nThe status is 'close', when subsequent disbursment document is posted.")
    account_move_id = fields.Many2one('account.move', string='Journal Entry', ondelete='restrict', copy=False, readonly=True)
    payment_state = fields.Selection(related='account_move_id.payment_state')
    amount_paid = fields.Float('Amount Paid', compute='_compute_from_account_move', store=True)
    

    res_id = fields.Integer(string="Related Document ID", readonly=True)
    model = fields.Char(string="Related Document Model", readonly=True)
    res_name = fields.Char(string="Reference", readonly=True)

    # --------------------------------------------------------
    # ----------------------- Methods ------------------------
    # --------------------------------------------------------
    @api.depends('account_move_id','account_move_id.payment_state')
    #@api.onchange('account_move_id.payment_state')
    def _compute_state(self):
        #raise UserError('hello')
        for line in self:
            if line.account_move_id:
                if line.account_move_id.payment_state in ('paid','in_payment'):
                    line.state = 'close'
                else:
                    line.state = 'pending'
            elif not loan.state:
                loan.state = 'draft'

    @api.depends('account_move_id','account_move_id.payment_state')
    def _compute_from_account_move(self):
        for line in self:
            if line.account_move_id.payment_state in ('paid','in_payment'):
                line.amount_paid = line.account_move_id.amount_total_signed - line.account_move_id.amount_residual_signed
            else:
                line.amount_paid = 0
            
class HrLoanDocuments(models.Model):
    _name = 'hr.loan.document'
    _description = 'Loan Documents'

    name = fields.Char(string='Document Name', readonly=True)
    doc_desc = fields.Char(string="Document")
    is_mandatory = fields.Boolean(string='Is Mandatory', default=False, readonly=True)
    attachment = fields.Binary(string='Attachment', attachment=True)
    loan_id = fields.Many2one('hr.loan', string='Loan', ondelete='cascade')

    def _message_post_attach_document(self, document, message):
        attachment = document.attachment
        if attachment:
            # Create an attachment record linked to the message
            attachment_data = {
                'name': document.name,
                'res_model': 'mail.message',
                'res_id': message.id,
                'datas': attachment,
            }
            self.env['ir.attachment'].create(attachment_data)

    @api.model
    def create(self, vals):
        document = super(HrLoanDocuments, self).create(vals)

        # Create a message and attach the document to it
        if document.attachment:
            loan_message = document.loan_id.message_post(
                body="Document Attached: %s" % document.name,
                attachment_ids=[],
                subtype_id=self.env['mail.message.subtype'].search([('name', '=', 'Note')]).id,
            )
            self._message_post_attach_document(document, loan_message)

        return document






