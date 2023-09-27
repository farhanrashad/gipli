# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime, timedelta, time
from pytz import timezone, UTC
from odoo.tools import date_utils
from odoo.addons.base.models.res_partner import _tz_get


class LeaveEncashment(models.Model):
    _name = 'hr.leave.encash'
    _description = 'Leave Encashment'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    @api.model
    def _default_employee_id(self):
        return self.env.user.employee_id

    def _default_journal_id(self):
        default_company_id = self.default_get(['company_id'])['company_id']
        journal = self.env['account.journal'].search([('type', '=', 'purchase'), ('company_id', '=', default_company_id)], limit=1)
        return journal.id
        
    @api.model
    def _get_employee_id_domain(self):
        res = [('id', '=', 0)] # Nothing accepted by domain, by default
        if self.user_has_groups('hr_holidays.group_hr_holidays_user') or self.user_has_groups('account.group_account_user'):
            res = "['|', ('company_id', '=', False), ('company_id', '=', company_id)]"  # Then, domain accepts everything
        elif self.user_has_groups('hr_holidays.group_hr_holidays_manager') and self.env.user.employee_ids:
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

    READONLY_STATES = {
        'confirm': [('readonly', True)],
        'refuse': [('readonly', True)],
        'validate': [('readonly', True)],
        'validate1': [('readonly', True)],
        'post': [('readonly', True)],
        'done': [('readonly', True)],
    }
    name = fields.Char(string='', required=True, readonly=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, readonly=False, tracking=True, states=READONLY_STATES, default=_default_employee_id, check_company=True, domain= lambda self: self.env['hr.leave.encash']._get_employee_id_domain())
    holiday_status_id = fields.Many2one(
        "hr.leave.type", compute='_compute_holiday_status_from_employee_id', store=True, string="Time Off Type", required=True, readonly=False, states=READONLY_STATES,
        domain="[('company_id', '=?', employee_company_id), '|', ('requires_allocation', '=', 'no'), ('has_valid_allocation', '=', True)]", tracking=True)
    leave_type_request_unit = fields.Selection(related='holiday_status_id.request_unit', readonly=True)
    validation_type = fields.Selection(string='Validation Type', related='holiday_status_id.leave_validation_type', readonly=False)

    active = fields.Boolean(default=True, readonly=True)
    first_approver_id = fields.Many2one(
        'hr.employee', string='First Approval', readonly=True, copy=False,
        help='This area is automatically filled by the user who validate the time off')
    second_approver_id = fields.Many2one(
        'hr.employee', string='Second Approval', readonly=True, copy=False,
        help='This area is automatically filled by the user who validate the time off with second level (If time off type need second validation)')
    can_reset = fields.Boolean('Can reset', compute='_compute_can_reset')
    can_approve = fields.Boolean('Can Approve', compute='_compute_can_approve')
    can_cancel = fields.Boolean('Can Cancel', compute='_compute_can_cancel')
    
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_from_employee_id')
    job_id = fields.Many2one('hr.job', string='Job', compute='_compute_from_employee_id')
    contract_id = fields.Many2one('hr.contract', string='Contract', compute='_compute_from_employee_id')
    user_id = fields.Many2one('res.users', 'Manager', compute='_compute_from_employee_id', store=True, readonly=True, copy=False, states={'draft': [('readonly', False)]}, tracking=True)
    address_id = fields.Many2one('res.partner', compute='_compute_from_employee_id', store=True, readonly=False, copy=True, string="Employee Home Address", check_company=True)


    date = fields.Date(string='Date', default=fields.Date.today(), required=True, states=READONLY_STATES,)
    account_move_id = fields.Many2one('account.move', string='Journal Entry', ondelete='restrict', copy=False, readonly=True)
    accounting_date = fields.Date(
        string='Accounting Date',
        compute='_compute_accounting_date',
        store=True
    )
    journal_id = fields.Many2one('account.journal', string='Accounting Journal', readonly=True, check_company=True, domain="[('type', '=', 'purchase'), ('company_id', '=', company_id)]",
        default=_default_journal_id, help="The journal used when the request is done.")
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',                                 compute='_compute_currency_id', store=True, readonly=True)

    # duration
    number_of_days = fields.Float(
        'Number of Days', store=True, readonly=False, tracking=True, default=1, required=True,
        help='Duration in days. Reference field to use when necessary.')
    leave_avail = fields.Float(string='Available Leaves', compute='_compute_all_balance')
    leave_remain = fields.Float(string='Remaining Leaves', compute='_compute_all_balance')
    amount_total = fields.Float(string='Total Amount', compute='_compute_total', store=True)
    description = fields.Text(string='Description')
    
    journal_count = fields.Integer(string='Journal Count', compute='_compute_journal_count')
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved'),
        ('post', 'Posted'),
        ('done', 'Done'),
        ], string='Status', compute='_compute_state', store=True, tracking=True, copy=False, readonly=False,
        help="The status is set to 'To Submit', when a time off request is created." +
        "\nThe status is 'To Approve', when request is confirmed by user." +
        "\nThe status is 'Refused', when request is refused by manager." +
        "\nThe status is 'Approved', when request is approved by manager.")

    @api.depends('company_id.currency_id')
    def _compute_currency_id(self):
        for sheet in self:
            # Deal with a display bug when there is a company currency change after creation of the expense sheet
            if not sheet.currency_id or sheet.state not in {'post', 'done', 'cancel'}:
                sheet.currency_id = sheet.company_id.currency_id

    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for record in self:
            record.address_id = record.employee_id.sudo().address_home_id
            record.department_id = record.employee_id.department_id
            record.job_id = record.employee_id.job_id
            record.contract_id = record.employee_id.contract_id
            record.user_id = record.employee_id.parent_id.user_id

    @api.depends('employee_id')
    def _compute_holiday_status_from_employee_id(self):
        for holiday in self:
            holiday.employee_id.parent_id = holiday.employee_id.parent_id.id
            if holiday.holiday_status_id.requires_allocation == 'no':
                continue
            if not holiday.employee_id:
                holiday.holiday_status_id = False
            elif holiday.employee_id.user_id != self.env.user and holiday._origin.employee_id != holiday.employee_id:
                if holiday.employee_id and not holiday.holiday_status_id.with_context(employee_id=holiday.employee_id.id).has_valid_allocation:
                    holiday.holiday_status_id = False
                    
    @api.depends('account_move_id.date')
    def _compute_accounting_date(self):
        for record in self:
            record.accounting_date = record.account_move_id.date

    @api.depends('holiday_status_id')
    def _compute_state(self):
        for leave in self:
            leave.state = 'draft' #'confirm' if leave.validation_type != 'no_validation' else 'draft'

    def _compute_all_balance(self):
        for record in self:
            allocation_ids = self.env['hr.leave.allocation'].search([('employee_id','=',record.employee_id.id),('holiday_status_id','=',record.holiday_status_id.id),('state','=','validate')])
            leave_ids = self.env['hr.leave'].search([('employee_id','=',record.employee_id.id),('holiday_status_id','=',record.holiday_status_id.id),('state','=','validate')])
            record.leave_avail = sum(allocation_ids.mapped('number_of_days_display')) - sum(leave_ids.mapped('number_of_days_display'))
            record.leave_remain = (sum(allocation_ids.mapped('number_of_days_display')) - sum(leave_ids.mapped('number_of_days_display'))) - record.number_of_days 



    @api.depends('state', 'employee_id', 'department_id')
    def _compute_can_reset(self):
        for holiday in self:
            try:
                holiday._check_approval_update('draft')
            except (AccessError, UserError):
                holiday.can_reset = False
            else:
                holiday.can_reset = True
    @api.depends('state', 'employee_id', 'department_id')
    def _compute_can_approve(self):
        for holiday in self:
            try:
                if holiday.state == 'confirm' and holiday.validation_type == 'both':
                    holiday._check_approval_update('validate1')
                else:
                    holiday._check_approval_update('validate')
            except (AccessError, UserError):
                holiday.can_approve = False
            else:
                holiday.can_approve = True
    @api.depends_context('uid')
    @api.depends('state', 'employee_id')
    def _compute_can_cancel(self):
        now = fields.Datetime.now()
        for leave in self:
            leave.can_cancel = leave.id and leave.employee_id.user_id == self.env.user and leave.state == 'validate' and leave.date_from and leave.date_from > now

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        if self.env.is_superuser():
            return

        current_employee = self.env.user.employee_id
        is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')

        for holiday in self:
            val_type = holiday.validation_type

            if not is_manager and state != 'confirm':
                if state == 'draft':
                    if holiday.state == 'refuse':
                        raise UserError(_('Only a Time Off Manager can reset a refused leave.'))
                    if holiday.date_from and holiday.date_from.date() <= fields.Date.today():
                        raise UserError(_('Only a Time Off Manager can reset a started leave.'))
                    if holiday.employee_id != current_employee:
                        raise UserError(_('Only a Time Off Manager can reset other people leaves.'))
                else:
                    if val_type == 'no_validation' and current_employee == holiday.employee_id:
                        continue
                    # use ir.rule based first access check: department, members, ... (see security.xml)
                    holiday.check_access_rule('write')

                    # This handles states validate1 validate and refuse
                    if holiday.employee_id == current_employee:
                        raise UserError(_('Only a Time Off Manager can approve/refuse its own requests.'))

                    if (state == 'validate1' and val_type == 'both') and holiday.holiday_type == 'employee':
                        if not is_officer and self.env.user != holiday.employee_id.leave_manager_id:
                            raise UserError(_('You must be either %s\'s manager or Time off Manager to approve this leave') % (holiday.employee_id.name))

                    if (state == 'validate' and val_type == 'manager') and self.env.user != (holiday.employee_id | holiday.sudo().employee_ids).leave_manager_id:
                        if holiday.employee_id:
                            employees = holiday.employee_id
                        else:
                            employees = ', '.join(holiday.employee_ids.filtered(lambda e: e.leave_manager_id != self.env.user).mapped('name'))
                        raise UserError(_('You must be %s\'s Manager to approve this leave', employees))

                    if not is_officer and (state == 'validate' and val_type == 'hr') and holiday.holiday_type == 'employee':
                        raise UserError(_('You must either be a Time off Officer or Time off Manager to approve this leave'))     
            
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'leave.enchasement') or _('New')
        res = super(LeaveEncashment, self).create(vals)
        return res

    def _compute_journal_count(self):
        for record in self:
            journal_total = self.env['account.move'].search_count([('id', '=', record.account_move_id.id)])
            record.journal_count = journal_total

    @api.depends('number_of_days', 'contract_id')
    def _compute_total(self):
        for record in self:
            if record.contract_id:
                wage = record.contract_id.wage
                if wage:
                    days = int(record.number_of_days)  # Extract integer part (days)
                    hours = (record.number_of_days - days) * 8  # Extract decimal part (hours)
                    
                    daily_wage = wage / 30  # Assuming 30 days in a month
                    total_wage = (days + hours/8) * daily_wage  # Calculate total wage
                    
                    record.amount_total = total_wage
                else:
                    record.amount_total = 0.0
            else:
                record.amount_total = 0.0
                



    def action_draft(self):
        self.write({'state': 'draft'})

    def action_confirm(self):
        self.write({'state': 'draft'})

    def action_validate(self):
        self.write({'state': 'draft'})
        
    def action_approve(self):
        self.write({'state': 'confirm'})
        return True
        

    def action_paid(self):
        self.write({'state': 'paid'})
        for rec in self:
            journal_rec = self.env['account.move'].search([])
            values = {
                'number': rec.bank_number,
                'employee_id': rec.employee_id.id,
                'due_date': rec.date,
                'state': rec.state,
                'total': rec.total,
            }
            journal_rec.create(values)

    def action_refuse(self):
        self.write({'state': 'cancel'})
        
    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_journal_entry(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Journal Entry',
            'view_mode': 'tree,form',
            'target': 'current',
            'res_model': 'account.move',
            'domain': [('id', '=', self.account_move_id.id)],
            'context': "{'create': False}"
        }
