# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class LeaveEncashment(models.Model):
    _name = 'leave.encashment'
    _description = 'Leave Encashment'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin', 'avatar.mixin']

    name = fields.Char(string='', required=True, readonly=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    department_id = fields.Many2one('hr.department', string='Department', required=True)
    job_id = fields.Many2one('hr.job', string='Job', required=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', required=True)
    date = fields.Date(string='Date', default=fields.Date.today())
    journal = fields.Selection(
        string='Journal',
        selection=[('bank', 'Bank'),
                   ('by_hand', 'By Hand'), ],
        required=False, default='bank')
    bank_number = fields.Char(string='Bank Number')
    enchase_type = fields.Selection(
        string='Enchase Type',
        selection=[('daily_salary', 'Daily Salary'),
                   ('fixed_amount', 'Fixed Amount'), ],
        required=False, default='fixed_amount')
    leave = fields.Float(string='Leave')
    amount = fields.Float(string='Amount', required=True)
    working_days = fields.Integer(string='Working Days')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True)
    total = fields.Float(string='Total', compute='_compute_total', store=True)
    description = fields.Text(string='Description')
    allocation_id = fields.Many2one('hr.leave.allocation', string='Leave Allocation')
    remaining_leave = fields.Integer(string='Remaining Leave', compute='_compute_remaining_leave', store=True)
    encasenmet_leave = fields.Integer(string='Encasement Leave', compute='_compute_encasenmet_leave', store=True)
    journal_count = fields.Integer(string='Journal Count', compute='_compute_journal_count')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled')
    ], string='State', default='draft')

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

    @api.depends('leave', 'amount')
    def _compute_total(self):
        for record in self:
            record.total = record.leave * record.amount

    @api.depends('employee_id')
    def _compute_remaining_leave(self):
        for record in self:
            leave_rec = self.env['hr.leave.allocation'].search(
                [('employee_id', '=', record.employee_id.id), ('state', '=', 'validate')])
            record.remaining_leave = leave_rec.number_of_days - record.leave

    @api.depends('leave')
    def _compute_encasenmet_leave(self):
        for record in self:
            record.remaining_leave = record.leave

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
