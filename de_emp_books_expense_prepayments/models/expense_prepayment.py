# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero


class ExpensePrepaymentType(models.Model):
    _name = "hr.expense.prepayment.type"
    _description = "Expense Prepayment Category"

    name = fields.Char(string='Name', required=True, translate=True)
    account_id = fields.Many2one('account.account', string='Account', readonly=False, required=True,
                                 domain="[('reconcile', '=', True)]", ondelete='restrict')


class HRExpensePrepayment(models.Model):
    """
        Here are the rights associated with the prepayment request for expense flow

        Action       Group                   Restriction
        =================================================================================
        Submit      Employee                Only his own
                    Officer                 If he is expense manager of the employee, manager of the employee
                                             or the employee is in the department managed by the officer
                    Manager                 Always
        Approve     Officer                 Not his own and he is expense manager of the employee, manager of the employee
                                             or the employee is in the department managed by the officer
                    Manager                 Always
        Post        Anybody                 State = approve and journal_id defined
        Done        Anybody                 State = approve and journal_id defined
        Cancel      Officer                 Not his own and he is expense manager of the employee, manager of the employee
                                             or the employee is in the department managed by the officer
                    Manager                 Always
        =================================================================================
    """
    _name = "hr.expense.prepayment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Prepayment Request for Expense"
    _order = "date desc, id desc"
    _check_company_auto = True

    @api.model
    def _default_employee_id(self):
        return self.env.user.employee_id

    @api.model
    def _default_journal_id(self):
        """ The journal is determining the company of the accounting entries generated from expense. We need to force journal company and expense sheet company to be the same. """
        default_company_id = self.default_get(['company_id'])['company_id']
        journal = self.env['account.journal'].search(
            [('type', '=', 'purchase'), ('company_id', '=', default_company_id)], limit=1)
        return journal.id

    @api.model
    def _get_employee_id_domain(self):
        res = [('id', '=', 0)]  # Nothing accepted by domain, by default
        if self.user_has_groups('hr_expense.group_hr_expense_user') or self.user_has_groups(
                'account.group_account_user'):
            res = "['|', ('company_id', '=', False), ('company_id', '=', company_id)]"  # Then, domain accepts everything
        elif self.user_has_groups('hr_expense.group_hr_expense_team_approver') and self.env.user.employee_ids:
            user = self.env.user
            employee = self.env.user.employee_id
            res = [
                '|', '|', '|',
                ('department_id.manager_id', '=', employee.id),
                ('parent_id', '=', employee.id),
                ('id', '=', employee.id),
                ('expense_manager_id', '=', user.id),
                '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id),
            ]
        elif self.env.user.employee_id:
            employee = self.env.user.employee_id
            res = [('id', '=', employee.id), '|', ('company_id', '=', False),
                   ('company_id', '=', employee.company_id.id)]
        return res

    name = fields.Char('Prepayment Request Summary', required=True, tracking=True)

    ref = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True,
                      default=lambda self: _('New'))

    date = fields.Date(string='Requested Date', required=True, default=fields.Date.context_today, readonly=True,
                       states={'draft': [('readonly', False)]}, )

    accounting_date = fields.Date(readonly=True,
                                  states={'draft': [('readonly', False)], 'submit': [('readonly', False)],
                                          'refused': [('readonly', False)]}, default=fields.Date.context_today,
                                  string="Accounting Date")

    employee_id = fields.Many2one('hr.employee', compute='_compute_employee_id', string="Employee", store=True,
                                  required=True, readonly=True, tracking=True, states={'draft': [('readonly', False)]},
                                  default=_default_employee_id, domain=lambda self: self._get_employee_id_domain(),
                                  check_company=True)

    user_id = fields.Many2one('res.users', 'Manager', compute='_compute_from_employee_id', store=True, readonly=True,
                              copy=False, states={'draft': [('readonly', False)]}, tracking=True, domain=lambda self: [
            ('groups_id', 'in', self.env.ref('hr_expense.group_hr_expense_team_approver').id)])

    manager_id = fields.Many2one('hr.employee', string='Manager', related='employee_id.parent_id')
    department_id = fields.Many2one('hr.department', compute='_compute_from_employee_id', store=True, readonly=True,
                                    copy=False, string='Department')
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', store=True, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]}, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.company.currency_id)
    total_amount = fields.Monetary('Total Amount', currency_field='currency_id', compute='_compute_amount', store=True,
                                   tracking=True)
    total_amount_approved = fields.Monetary('Approved Amount', currency_field='currency_id', compute='_compute_amount',
                                            store=True, tracking=True)

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('submit', 'Submitted'),
        ('approved', 'Approved'),
        ('post', 'Posted'),
        ('done', 'Paid'),
        ('reconciled', 'Reconciled'),
        ('refused', 'Refused')
    ], string='Status', copy=False, index=True, compute='_compute_state', store=True, default='draft',
        help="Status of the Avances.")

    description = fields.Text('Notes...', readonly=True,
                              states={'draft': [('readonly', False)], 'submit': [('readonly', False)],
                                      'refused': [('readonly', False)]})

    address_id = fields.Many2one('res.partner', compute='_compute_from_employee_id', store=True, readonly=False,
                                 copy=True, string="Employee Home Address", check_company=True,
                                 states={'done': [('readonly', True)], 'reconcile': [('readonly', True)]})

    journal_id = fields.Many2one('account.journal', string='Journal', domain="[('type','=','purchase')]",
                                 default=_default_journal_id)
    account_move_id = fields.Many2one('account.move', string='Journal Entry', ondelete='restrict', copy=False,
                                      readonly=True)
    payment_state = fields.Selection('Payment State', related='account_move_id.payment_state')
    account_amount_residual = fields.Monetary('Residual Amount', compute='_compute_residual_amount')
    can_reset = fields.Boolean('Can Reset', compute='_compute_can_reset')

    expense_prepayment_line_ids = fields.One2many('hr.expense.prepayment.line', 'expense_prepayment_id',
                                                  string='Expense Prepayment Lines', copy=False)

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].get('hr.expense.prepayment') or ' '
        res = super(HRExpensePrepayment, self).create(vals)
        return res

    def _compute_residual_amount(self):
        self.account_amount_residual = sum(self.account_move_id.line_ids.mapped('amount_residual'))

    @api.depends('account_move_id', 'account_move_id.payment_state', 'expense_prepayment_line_ids.state',
                 'account_amount_residual')
    def _compute_state(self):
        # status = self.state
        residual_amount = 0
        for request in self:
            state_lst = request.mapped('expense_prepayment_line_ids.state')
            # residual_amount = sum(request.account_move_id.line_ids.mapped('amount_residual')
            residual_amount = sum(request.account_move_id.line_ids.mapped('amount_residual'))
            # line_ids = request.mapped('request.account_move_id.line_ids')
            # sum(others_lines.mapped('amount_currency'))

            # if state_lst:
            #    if state_lst.count('reconciled'):
            #        status = 'reconciled'
            if request.account_move_id:
                if request.payment_state in ['in_payment', 'paid']:
                    if request.account_amount_residual == 0:
                        status = 'reconciled'
                    else:
                        status = 'done'
                elif request.payment_state == 'not_paid':
                    status = 'post'
                else:
                    status = request.state  # 'draft'
            else:
                status = request.state

            request.state = status

    @api.depends('account_move_id.payment_state', 'account_move_id', 'expense_prepayment_line_ids.state')
    def _compute_state1(self):
        # if all(picking.state not in ('done','cancel') for picking in order.picking_ids.filtered(lambda p: p.picking_type_id.id == order.picking_type_id.id)):

        if all(line.state == 'reconciled' for line in
               self.expense_prepayment_line_ids.filtered(lambda p: p.state != False)):
            self.state = 'reconciled'
        else:
            # for move in self.account_move_id:
            if self.payment_state == 'in_payment':
                self.state = 'done'

    @api.depends('expense_prepayment_line_ids.amount')
    def _compute_amount(self):
        for adv in self:
            adv.total_amount = sum(adv.expense_prepayment_line_ids.mapped('amount'))
            adv.total_amount_approved = sum(adv.expense_prepayment_line_ids.mapped('amount_approved'))

    def _compute_can_reset(self):
        is_prepayment_user = self.user_has_groups('hr_expense.group_hr_expense_team_approver')
        for adv in self:
            adv.can_reset = is_prepayment_user if is_prepayment_user else adv.employee_id.user_id == self.env.user

    def unlink(self):
        for adv in self:
            if adv.state not in ['draft']:
                raise UserError(_('You cannot delete a posted or approved request.'))
        return super(HRExpensePrepayment, self).unlink()

    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for adv in self:
            adv.address_id = adv.employee_id.sudo().address_home_id
            adv.department_id = adv.employee_id.department_id
            adv.user_id = adv.employee_id.expense_manager_id or adv.employee_id.parent_id.user_id

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'approve':
            return self.env.ref('de_emp_books_expense_prepayments.mt_expense_prepayment_approved')
        elif 'state' in init_values and self.state == 'cancel':
            return self.env.ref('de_emp_books_expense_prepayments.mt_expense_prepayment_refused')
        elif 'state' in init_values and self.state == 'done':
            return self.env.ref('de_emp_books_expense_prepayments.mt_expense_prepayment_paid')
        return super(HRExpensePrepayment, self)._track_subtype(init_values)

    def _message_auto_subscribe_followers(self, updated_values, subtype_ids):
        res = super(HRExpensePrepayment, self)._message_auto_subscribe_followers(updated_values, subtype_ids)
        if updated_values.get('employee_id'):
            employee = self.env['hr.employee'].browse(updated_values['employee_id'])
            if employee.user_id:
                res.append((employee.user_id.partner_id.id, subtype_ids, False))
        return res

    def action_submit_prepayment(self):
        for adv in self.expense_prepayment_line_ids:
            if adv.amount == 0:
                raise UserError(_("The request cannot submit for 0 amount."))
            elif adv.amount < 0:
                raise UserError(_("The request cannot submit for negative amount."))
        self.write({'state': 'submit'})
        self.activity_update()

    @api.depends('job_id')
    def compute_from_job(self):
        amount = 0
        for adv in self:
            if adv.job_id.prepayment_limit_method == 'percentage':
                amount = adv.employee_id.contract_id.wage * (adv.job_id.amount / 100)
            else:
                amount = adv.job_id.fixed_amount
            adv.applicable_amount = amount

    def _get_responsible_for_approval(self):
        if self.user_id:
            return self.user_id
        elif self.employee_id.parent_id.user_id:
            return self.employee_id.parent_id.user_id
        elif self.employee_id.department_id.manager_id.user_id:
            return self.employee_id.department_id.manager_id.user_id
        return self.env['res.users']

    def activity_update(self):
        for adv in self.filtered(lambda adv: adv.state == 'submit'):
            self.activity_schedule(
                'de_emp_books_expense_prepayments.mail_act_expense_prepayment_approval',
                user_id=adv.sudo()._get_responsible_for_approval().id or self.env.user.id)
        self.filtered(lambda hol: hol.state == 'approve').activity_feedback(
            ['de_emp_books_expense_prepayments.mail_act_expense_prepayment_approval'])
        self.filtered(lambda hol: hol.state in ('draft', 'cancel')).activity_unlink(
            ['de_emp_books_expense_prepayments.mail_act_expense_prepayment_approval'])

    def approve_prepayment(self):
        if not self.user_has_groups('hr_expense.group_hr_expense_team_approver'):
            raise UserError(_("Only Managers and HR Officers can approve prepayments"))
        elif not self.user_has_groups('hr_expense.group_hr_expense_manager'):
            current_managers = self.employee_id.expense_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot approve your own prepayment request"))

            if not self.env.user in current_managers and not self.user_has_groups(
                    'hr_expense.group_hr_expense_user') and self.employee_id.prepayment_manager_id != self.env.user:
                raise UserError(_("You can only approve your department prepayments"))

        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no prepayment requests to approve.'),
                'type': 'warning',
                'sticky': False,  # True/False will display for few seconds if false
            },
        }
        state = ''
        filtered_prepayment = self.filtered(lambda s: s.state in ['submit', 'draft'])
        if not filtered_prepayment:
            return notification
        for adv in filtered_prepayment:
            adv.write({
                'state': 'approved',
                'user_id': adv.user_id.id or self.env.user.id
            })
        notification['params'].update({
            'title': _('The prepayment requests were successfully approved.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })

        self.activity_update()
        return notification

    def _compute_prepayment_balance(self):
        for line in self:
            payslip_id = self.env['hr.payslip'].search(
                [('employee_id', '=', line.employee_id.id), ('date_from', '<=', line.date),
                 ('date_to', '>=', line.date), ('state', '=', 'done')], limit=1)
            payslip_input_id = self.env['hr.payslip.input']
            domain = [('payslip_id', '=', payslip_id.id)]

            where_query = payslip_input_id._where_calc(domain)
            payslip_input_id._apply_ir_rules(where_query, 'read')
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            select = "SELECT SUM(amount) from " + from_clause + " where " + where_clause

            self.env.cr.execute(select, where_clause_params)
            line.amount_ded = self.env.cr.fetchone()[0] or 0.0
            line.balance = line.amount - line.amount_ded

    def reset_prepayment_request(self):
        if not self.can_reset:
            raise UserError(_("Only HR Officers or the concerned employee can reset to draft."))
        self.write({'state': 'draft'})
        self.activity_update()
        return True

    def refuse_prepayment(self, reason):
        if not self.user_has_groups('hr_expense.group_hr_expense_team_approver'):
            raise UserError(_("Only Managers and HR Officers can approve expenses"))
        elif not self.user_has_groups('hr_expense.group_hr_expense_manager'):
            current_managers = self.employee_id.expense_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot refuse your own expenses"))

            if not self.env.user in current_managers and not self.user_has_groups(
                    'hr_expense.group_hr_expense_user') and self.employee_id.expense_manager_id != self.env.user:
                raise UserError(_("You can only refuse your department expenses"))

        self.write({'state': 'refused'})
        for adv in self:
            adv.message_post_with_view('de_emp_books_expense_prepayments.hr_expense_prepayment_template_refuse_reason',
                                       values={'reason': reason, 'is_sheet': True, 'name': adv.name})
        self.activity_update()

    def action_create_bill(self):
        if not self.journal_id.id:
            raise UserError(_("The journal must be set on approved request"))

        if not self.address_id.id:
            raise UserError(_("The partner must be set on approved request"))
        res = self._create_bill()
        self.update({
            'state': 'post',
        })

    def _create_bill(self):
        invoice = self.env['account.move']
        lines_data = []
        for adv in self.expense_prepayment_line_ids:
            lines_data.append([0, 0, {
                'name': str(adv.name) + ' ' + str(adv.account_id.name),
                'hr_expense_prepayment_line_id': adv.id,
                'price_unit': adv.amount or 0.0,
                'quantity': 1,
                'account_id': adv.account_id.id
            }])
        self.account_move_id = invoice.create({
            'move_type': 'in_invoice',
            'invoice_date': fields.Datetime.now(),
            'partner_id': self.address_id.id,
            'currency_id': self.currency_id.id,
            'journal_id': self.journal_id.id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.address_id.property_supplier_payment_term_id.id,
            'narration': self.name,
            'invoice_user_id': self.user_id.id,
            'invoice_line_ids': lines_data,
        })
        self.account_move_id._post()
        return invoice


class HRExpensePrepaymentLine(models.Model):
    _name = "hr.expense.prepayment.line"
    _description = "Expense Prepayment Line"
    _order = "id desc"
    _check_company_auto = True

    expense_prepayment_id = fields.Many2one('hr.expense.prepayment', string="Expense Prepayment", readonly=True,
                                            copy=False)
    employee_id = fields.Many2one('hr.employee', related='expense_prepayment_id.employee_id')
    date = fields.Date(related='expense_prepayment_id.date')

    name = fields.Char('Description', compute='_compute_name', store=True, required=True, copy=True,
                       states={'draft': [('readonly', False)], 'submit': [('readonly', False)],
                               'refused': [('readonly', False)]})

    prepayment_type_id = fields.Many2one('hr.expense.prepayment.type', string='Prepayment Type', copy=False,
                                         required=True)
    account_id = fields.Many2one('account.account', string='Account', related='prepayment_type_id.account_id')

    amount = fields.Monetary("Amount", currency_field='currency_id', required=True, copy=False)
    amount_approved = fields.Monetary("Approved Amount", currency_field='currency_id', copy=False)
    amount_residual = fields.Monetary("Residual Amount", currency_field='currency_id', copy=False,
                                      compute='_compute_residual_amount')
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                  related='expense_prepayment_id.currency_id')
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 related='expense_prepayment_id.company_id')

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('submit', 'Submitted'),
        ('approved', 'Approved'),
        ('post', 'Posted'),
        ('done', 'Paid'),
        ('reconciled', 'Reconciled'),
        ('refused', 'Refused')
    ], compute='_compute_state', string='Status', copy=False, index=True, readonly=True, store=True, default='draft',
        help="Status of the prepayment.")

    note = fields.Char(string='Remarks')
    is_editable = fields.Boolean("Is Editable By Current User", compute='_compute_is_editable')
    is_amount_approved_editable = fields.Boolean("Reference Is Editable By Current User",
                                                 compute='_compute_is_amount_approved_editable')

    def unlink(self):
        for adv in self:
            if adv.state not in ['draft', 'refused']:
                raise UserError(_('You cannot delete a posted or approved request.'))
        return super(HRExpensePrepaymentLine, self).unlink()

    def write(self, vals):
        if 'prepayment_type_id' in vals or 'account_id' in vals or 'amount' in vals or 'name' in vals:
            if any(not adv.is_editable for adv in self):
                raise UserError(_('You are not authorized to edit this prepayment payment request.'))
        if 'amount_approved' in vals:
            if any(not adv.is_amount_approved_editable for adv in self):
                raise UserError(_('You are not authorized to edit approved amount.'))
        return super(HRExpensePrepaymentLine, self).write(vals)

    @api.depends('prepayment_type_id')
    def _compute_name(self):
        for line in self:
            if not line.name:
                line.name = line.prepayment_type_id.account_id.name

    @api.onchange('amount')
    def _onchange_amount(self):
        self.amount_approved = self.amount

    def _compute_residual_amount(self):
        amount = 0
        move_lines = self.env['account.move.line']
        for line in self:
            amount = 0
            move_lines = self.env['account.move.line'].search(
                [('hr_expense_prepayment_line_id', '=', line.id), ('account_id', '=', line.account_id.id)])
            for move in move_lines.filtered(lambda x: x.account_id.reconcile == True):
                amount += move.amount_residual
            line.amount_residual = amount

    @api.depends('expense_prepayment_id', 'expense_prepayment_id.account_move_id',
                 'expense_prepayment_id.account_move_id.payment_state', 'expense_prepayment_id.state',
                 'amount_residual')
    def _compute_state(self):
        for prepayment in self:
            if prepayment.expense_prepayment_id.account_move_id:
                if prepayment.amount_residual == 0:
                    prepayment.state = 'reconciled'
                elif prepayment.expense_prepayment_id.account_move_id.payment_state == 'not_paid':
                    prepayment.state = "post"
                elif prepayment.expense_prepayment_id.account_move_id.payment_state in ['in_payment', 'paid']:
                    prepayment.state = "done"
            else:
                if not prepayment.expense_prepayment_id or prepayment.expense_prepayment_id.state == 'draft':
                    prepayment.state = "draft"
                elif prepayment.expense_prepayment_id.state == "refused":
                    prepayment.state = "refused"
                elif prepayment.expense_prepayment_id.state == "approved":
                    prepayment.state = "approved"

    @api.depends('employee_id')
    def _compute_is_editable(self):
        is_account_manager = self.env.user.has_group('account.group_account_user') or self.env.user.has_group(
            'account.group_account_manager')
        is_approver = self.env.user.has_group('hr_expense.group_hr_expense_user') or self.env.user.has_group(
            'hr_expense.group_hr_expense_manager')

        for line in self:
            if line.state == 'draft':
                line.is_editable = True
            elif line.expense_prepayment_id.state == 'approve':
                line.is_editable = is_account_manager
            else:
                line.is_editable = False

    @api.depends('employee_id')
    def _compute_is_amount_approved_editable(self):
        is_approver = self.env.user.has_group('hr_expense.group_hr_expense_user') or self.env.user.has_group(
            'hr_expense.group_hr_expense_manager')
        for adv in self:
            if adv.state == 'submit' or adv.expense_prepayment_id.state in ['draft', 'submit']:
                adv.is_amount_approved_editable = True
            else:
                adv.is_amount_approved_editable = is_approver
