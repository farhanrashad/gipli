# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


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
    
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_from_employee_id')
    job_id = fields.Many2one('hr.job', string='Job', compute='_compute_from_employee_id')
    contract_id = fields.Many2one('hr.contract', string='Contract', compute='_compute_from_employee_id')
    user_id = fields.Many2one('res.users', 'Manager', compute='_compute_from_employee_id', store=True, readonly=True, copy=False, states={'draft': [('readonly', False)]}, tracking=True)
    address_id = fields.Many2one('res.partner', compute='_compute_from_employee_id', store=True, readonly=False, copy=True, string="Employee Home Address", check_company=True)


    date = fields.Date(string='Date', default=fields.Date.today())
    account_move_id = fields.Many2one('account.move', string='Journal Entry', ondelete='restrict', copy=False, readonly=True)
    accounting_date = fields.Date(
        string='Accounting Date',
        compute='_compute_accounting_date',
        store=True
    )
    journal_id = fields.Many2one('account.journal', string='Accounting Journal', states={'done': [('readonly', True)], 'post': [('readonly', True)]}, check_company=True, domain="[('type', '=', 'purchase'), ('company_id', '=', company_id)]",
        default=_default_journal_id, help="The journal used when the request is done.")
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', states={'draft': [('readonly', False)]},
                                  compute='_compute_currency_id', store=True, readonly=True)

    # duration
    number_of_days = fields.Float(
        'Number of Days', compute='_compute_from_holiday_status_id', store=True, readonly=False, tracking=True, default=1,
        help='Duration in days. Reference field to use when necessary.')
    number_of_days_display = fields.Float(
        'Duration (days)', compute='_compute_number_of_days_display',
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        help="If Accrual Allocation: Number of days allocated in addition to the ones you will get via the accrual' system.")
    number_of_hours_display = fields.Float(
        'Duration (hours)', compute='_compute_number_of_hours_display',
        help="If Accrual Allocation: Number of hours allocated in addition to the ones you will get via the accrual' system.")
    
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
        for sheet in self:
            sheet.accounting_date = sheet.account_move_id.date

    @api.depends('holiday_status_id')
    def _compute_state(self):
        for leave in self:
            leave.state = 'draft' #'confirm' if leave.validation_type != 'no_validation' else 'draft'

    @api.depends('holiday_status_id', 'allocation_type', 'number_of_hours_display', 'number_of_days_display', 'date_to')
    def _compute_from_holiday_status_id(self):
        accrual_allocations = self.filtered(lambda alloc: alloc.allocation_type == 'accrual' and not alloc.accrual_plan_id and alloc.holiday_status_id)
        accruals_dict = {}
        if accrual_allocations:
            accruals_read_group = self.env['hr.leave.accrual.plan'].read_group(
                [('time_off_type_id', 'in', accrual_allocations.holiday_status_id.ids)],
                ['time_off_type_id', 'ids:array_agg(id)'],
                ['time_off_type_id'],
            )
            accruals_dict = {res['time_off_type_id'][0]: res['ids'] for res in accruals_read_group}
        for allocation in self:
            allocation.number_of_days = allocation.number_of_days_display
            if allocation.type_request_unit == 'hour':
                allocation.number_of_days = allocation.number_of_hours_display / \
                    (allocation.employee_id.sudo().resource_calendar_id.hours_per_day \
                    or allocation.holiday_status_id.company_id.resource_calendar_id.hours_per_day \
                    or HOURS_PER_DAY)
            if allocation.accrual_plan_id.time_off_type_id.id not in (False, allocation.holiday_status_id.id):
                allocation.accrual_plan_id = False
            if allocation.allocation_type == 'accrual' and not allocation.accrual_plan_id:
                if allocation.holiday_status_id:
                    allocation.accrual_plan_id = accruals_dict.get(allocation.holiday_status_id.id, [False])[0]

    @api.depends('number_of_days')
    def _compute_number_of_days_display(self):
        for allocation in self:
            allocation.number_of_days_display = allocation.number_of_days
            
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'leave.enchasement') or _('New')
        res = super(LeaveEncashment, self).create(vals)
        return res

    def _compute_journal_count(self):
        for record in self:
            journal_total = self.env['journal.entry'].search_count([('employee_id', '=', record.employee_id.id)])
            record.journal_count = journal_total

    def _compute_total(self):
        for record in self:
            record.total = record.leave * record.amount

    @api.depends('employee_id')
    def _compute_remaining_leave(self):
        for record in self:
            leave_rec = self.env['hr.leave.allocation'].search(
                [('employee_id', '=', record.employee_id.id), ('state', '=', 'validate')])
            record.remaining_leave = 0 #leave_rec.number_of_days - record.leave

    @api.depends('leave')
    def _compute_encasenmet_leave(self):
        for record in self:
            record.encasenmet_leave = record.leave

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_approve(self):
        self.write({'state': 'approve'})

    def action_paid(self):
        self.write({'state': 'paid'})
        for rec in self:
            journal_rec = self.env['journal.entry'].search([])
            values = {
                'number': rec.bank_number,
                'employee_id': rec.employee_id.id,
                'due_date': rec.date,
                'state': rec.state,
                'total': rec.total,
            }
            journal_rec.create(values)

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_journal_entry(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Journal Entry',
            'view_mode': 'tree,form',
            'target': 'current',
            'res_model': 'journal.entry',
            'domain': [('employee_id', '=', self.employee_id.id)],
            'context': "{'create': False}"
        }
