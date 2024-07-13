# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)

class HrSuspended(models.Model):
    _name = 'hr.suspended'
    _rec_name = 'name'
    _description = 'Termination'
    _order = 'name asc, id desc'

    name = fields.Char(string="Name",related='employee_id.name', required=False, )

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True, )
    department_id = fields.Many2one(comodel_name="hr.department",string="Department")
    job_id = fields.Many2one(comodel_name="hr.job",string="Job Title")
    responsible_id = fields.Many2one(comodel_name="hr.employee", string="Responsible", required=False, )
    state = fields.Selection(string="State", selection=[('cancel', 'Cancel'), ('draft', 'Draft'),('approved', 'Approved'), ],default='draft', required=False, )
    date_from = fields.Date(string="Date From", required=False, )
    date_to = fields.Date(string="Date To", required=False, )
    approve_date = fields.Date(string="Approve Date", required=False, )
    reason = fields.Text(string="Reason", required=False, )

    # @api.model
    # def create(self,vals):
    #     vals['name'] = self.env['ir.sequence'].next_by_code('hr.suspended')
    #     return super(HrSuspended, self).create(vals)

    @api.onchange('employee_id')
    def onchange_employee(self):
        self.update({'department_id':self.employee_id.department_id.id,'job_id':self.employee_id.job_id.id})

    def action_cancel(self):
        return self.write({'state':'cancel'})

    def action_approved(self):
        self.employee_id.state = 'suspended'
        return self.write({'state':'approved','approve_date':fields.Date.today()})





