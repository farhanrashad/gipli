# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    state = fields.Selection(string="Employee State", selection=[('active', 'Active'),('suspended', 'Suspended'), ('terminated', 'Terminated')],default='active', required=False, )

    suspended_ids = fields.One2many(comodel_name="hr.suspended", inverse_name="employee_id", string="", required=False, )

    termination_id = fields.Many2one(comodel_name="hr.termination",compute='_compute_termination_id', string="Termination", required=False, )
    termination_date = fields.Date(string="Termination Date",related='termination_id.termination_date', required=False, )
    termination_reason = fields.Many2one(comodel_name='hr.termination.reason',string="Termination Reason",related='termination_id.reason', required=False, )

    # resignation_id = fields.Many2one(comodel_name="hr.resignation",compute='_compute_resignation_id', string="Resignation", required=False, )
    # resignation_date = fields.Date(string="Resignation Date",related='resignation_id.resign_date', required=False, )
    # resignation_reason = fields.Text(string="Resignation Reason",related='resignation_id.reason', required=False, )

    retirement_id = fields.Many2one(comodel_name="hr.retirement",compute='_compute_retirement_id', string="Retirement", required=False, )
    retirement_date = fields.Date(string="Retirement Date",related='retirement_id.retirement_date', required=False, )
    retirement_reason = fields.Text(string="Retirement Reason",related='retirement_id.reason', required=False, )

    def _compute_termination_id(self):
        termination = self.env['hr.termination']
        for employee in self:
            employee.termination_id = termination.search([('employee_id', '=', employee.id)], order='termination_date desc',
                                                   limit=1)

    def _compute_resignation_id(self):
        resignation = self.env['hr.resignation']
        for employee in self:
            employee.resignation_id = resignation.search([('employee_id', '=', employee.id)], order='resign_date desc',
                                                   limit=1)

    def _compute_retirement_id(self):
        retirement = self.env['hr.retirement']
        for employee in self:
            employee.retirement_id = retirement.search([('employee_id', '=', employee.id)], order='retirement_date desc',
                                                   limit=1)

    @api.model
    def retirement_notification(self):
        today = datetime.now().date()
        birth_start = today + relativedelta(years=-60)
        after_two_months = today + relativedelta(months=2)
        birth_end = after_two_months + relativedelta(years=-60)
        users = self.env.ref('centione_hr_end_service.group_end_of_service_notifications').users
        emails_list = users.mapped('email')
        emails_str = ','.join(emails_list)
        employees = self.search([
            ('state','=','active'),
            ('birthday','<=',str(birth_end)),
            ('birthday','>=',str(birth_start))
        ])
        for emp in employees:
            notification_temp = self.env.ref('centione_hr_end_service.mail_template_end_of_service')
            mail_id = notification_temp.with_context(mail_to=emails_str).send_mail(emp.id)

    def action_active(self):
        return self.write({'state':'active'})
