# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)


class HrTermination(models.Model):
    _name = 'hr.termination'
    _rec_name = 'name'
    _description = 'Termination'
    _order = 'name asc, id desc'

    name = fields.Char(string="Name", related='employee_id.name', required=False, )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True, )
    company_id = fields.Many2one('res.company', related='employee_id.company_id')
    franchise = fields.Many2one(related='employee_id.franchise', string='Franchise')
    department_id = fields.Many2one(comodel_name="hr.department", string="Department")
    job_id = fields.Many2one(comodel_name="hr.job", string="Job Title")
    state = fields.Selection(string="State",
                             selection=[('cancel', 'Cancel'), ('draft', 'Draft'), ('approved', 'Approved'), ],
                             default='draft', required=False, )
    request_date = fields.Date(string="Request Date", required=False, )
    approve_date = fields.Date(string="Approve Date", required=False, )
    termination_date = fields.Date(string="Termination Date", required=False, )
    reason = fields.Many2one(comodel_name='hr.termination.reason', string='Termination Reason')
    turnover_reason = fields.Many2one(comodel_name="turnover.reason", string="Reason", required=False, )
    end_incentive = fields.Float(string="End of Service Incentive", required=False, )
    end_incentive_month = fields.Float(string="End of Service Months",
                                       default=lambda self: self.env["ir.config_parameter"].get_param(
                                           "end_service_incentive"))
    num_custody = fields.Integer(string="", required=False, compute='compute_num_custody')
    is_incentive_calc = fields.Boolean(string="Is Incentive Calc",
                                       default=lambda self: self.env["ir.config_parameter"].get_param("is_calculated"))
    legal_leaves_incentive = fields.Float()
    company_currency_id = fields.Many2one(string='Company Currency', readonly=True,
                                          related='company_id.currency_id')
    hire_date = fields.Date(string="Hire Date", related='employee_id.hire_date', )
    last_wage = fields.Monetary('Last Wage', compute='_compute_amount', currency_field='company_currency_id',
                                help="Employee's monthly gross wage.")

    def _compute_amount(self):
        contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'close')],
                                              limit=1)
        if contract:
            self.last_wage = contract.wage
        else:
            self.last_wage = None

    def archive_employees(self):
        for rec in self:
            rec.employee_id.write({'active': False})

    def terminate_employees(self):
        for rec in self:
            rec.action_approved()

    @api.model
    def create(self, vals):
        # vals['name'] = self.env['ir.sequence'].next_by_code('hr.termination')
        res = super(HrTermination, self).create(vals)
        for rec in res:
            if rec.state == 'approved':
                rec.action_approved()
        return res

    @api.onchange('employee_id')
    def onchange_employee(self):
        self.update({'department_id': self.employee_id.department_id.id, 'job_id': self.employee_id.job_id.id})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_approved(self):
        custody = False
        # check if the employee did not return custody
        for custody in self.employee_id.employee_custody_ids:
            if not custody.return_date:
                custody = True
                raise ValidationError(_('Please Check The Custody Of This Employee'))

        wage_per_day = self.employee_id.contract_id.wage / 30.0
        legal_leaves_days = self.employee_id.remaining_leaves
        self.legal_leaves_incentive = wage_per_day * legal_leaves_days
        self.end_incentive += self.legal_leaves_incentive

        # cancel all employee's contracts
        self.employee_id.contract_id.date_end = self.termination_date
        self.employee_id.contract_id.end_incentive = self.end_incentive

        for contract in self.employee_id.contract_ids:
            if contract.state != 'close':
                contract.date_end = self.termination_date
                contract.state = 'close'
                contract.end_incentive = self.end_incentive
                contract.end_incentive_month = self.end_incentive_month
        self.employee_id.state = 'terminated'
        return self.write({'state': 'approved', 'approve_date': fields.Date.today()})

    def action_custody(self):
        ids = self.employee_id.employee_custody_ids.ids

        return {
            'name': "Employee Custody",
            'view_mode': 'tree,form',
            'res_model': 'hr.custody',
            'type': 'ir.actions.act_window',
            'domain': [("id", "in", ids)],
            # 'res_id': newid,
            'context': {'default_employee_id': self.employee_id.id},
        }

    def compute_num_custody(self):
        for rec in self:
            rec.num_custody = len(rec.employee_id.employee_custody_ids)


class TerminationReson(models.Model):
    _name = 'hr.termination.reason'

    name = fields.Char(string='Termination Reason')
