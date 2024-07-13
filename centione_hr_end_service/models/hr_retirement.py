# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)

class HrTermination(models.Model):
    _name = 'hr.retirement'
    _rec_name = 'name'
    _description = 'Termination'
    _order = 'name asc, id desc'

    name = fields.Char(string="Name",related='employee_id.name', required=False, )

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True,domain=[('state','=','active')] )
    department_id = fields.Many2one(comodel_name="hr.department",string="Department")
    job_id = fields.Many2one(comodel_name="hr.job",string="Job Title")
    state = fields.Selection(string="State", selection=[('cancel', 'Cancel'), ('draft', 'Draft'),('approved', 'Approved'), ],default='draft', required=False, )
    retirement_date = fields.Date(string="Retirement Date", required=False, )
    approve_date = fields.Date(string="Approve Date", required=False, )
    reason = fields.Text(string="Reason", required=False, )
    end_incentive = fields.Float(string="End of Service Incentive",  required=False, )
    num_custody = fields.Integer(string="", required=False,compute='compute_num_custody' )
    is_incentive_calc = fields.Boolean(string="Is Incentive Calc",default=lambda self:self.env["ir.config_parameter"].get_param("is_calculated") )

    @api.onchange('employee_id')
    def onchange_employee(self):
        self.update({'department_id':self.employee_id.department_id.id,'job_id':self.employee_id.job_id.id})
        if self.employee_id and self.employee_id.birthday:
            birth_date = fields.Datetime.from_string(self.employee_id.birthday)
            retired_date = birth_date.replace(year=birth_date.year + 60)
            self.update({'retirement_date':str(retired_date.date())})


    def action_approved(self):
        custody = False
        # check if the employee did not return custody
        for custody in self.employee_id.employee_custody_ids:
            if not custody.return_date:
                custody = True
                raise ValidationError(_('Please Check The Custody Of This Employee'))

        self.employee_id.state = 'retired'
        if self.employee_id.contract_id:
            self.employee_id.contract_id.date_end = self.retirement_date
            self.employee_id.contract_id.end_incentive = self.end_incentive

            # cancel all employee's contracts
        for contract in self.employee_id.contract_ids:
            if contract.state != 'cancel':
                contract.date_end = self.retirement_date
                contract.state = 'cancel'
                # contract.end_incentive = self.end_incentive
        return self.write({'state':'approved','approve_date':fields.Date.today()})

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








