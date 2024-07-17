# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    manager_id = fields.Many2one('hr.employee', string='Manager', tracking=True,
                                 domain="['|', ('company_id', '=', False),'|',('allowed_companies', '=',company_id ),('company_id', '=', company_id)]")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    allowed_companies = fields.Many2many('res.company')
    from_hr = fields.Boolean(
        string='Created From Hr',
        required=False)
    employee_database_id = fields.Integer(string='Employee Database Id')
    employee_hire_date = fields.Date(string='Employee Hire Date')
    employee_resignation_date = fields.Date(string='Employee Resignation Date')
    employee_state = fields.Char(string='Employee Status')

    def get_old_emp_data(self):
        for rec in self:
            record = self.env['hr.employee'].sudo().search([('zk_emp_id','=',rec.ref)],limit=1)
            self.sudo().write({'name': record.name,
                                                                          'email': record.work_email,
                                                                          'company_id': record.company_id.id,
                                                                          'company_type': 'person',
                                                                          'phone': record.phone_num,
                                                                          'mobile': record.work_phone or record.mobile_phone,
                                                                          'email': record.work_email,
                                                                          'x_studio_arabic_name': record.employee_arabic_name,
                                                                          'employee_database_id': record.id,
                                                                          'employee_hire_date': record.hire_date,
                                                                          'employee_resignation_date': record.resignation_date,
                                                                          'employee_state': record.state,
                                                                          'id_def': record.identification_id	,
                                                                          'street': record.address_home_id.street	 ,
                                                                          })



class HrTermination(models.Model):
    _inherit = 'hr.termination'

    allowed_companies = fields.Many2many('res.company', related='employee_id.allowed_companies')



class HrContract(models.Model):
    _inherit = 'hr.contract'

    allowed_companies = fields.Many2many('res.company', related='employee_id.allowed_companies')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    allowed_companies = fields.Many2many('res.company')
    parent_id = fields.Many2one('hr.employee', 'Manager', compute="_compute_parent_id", store=True, readonly=False,
                                domain="['|', ('company_id', '=', False),'|', '|',('allowed_companies', 'in', allowed_companies),('company_id', 'in', allowed_companies),'|', ('allowed_companies', 'in', company_id),('company_id', '=', company_id)]")

    @api.depends('department_id')
    def _compute_parent_id(self):
        for employee in self.filtered('department_id.manager_id'):
            employee.parent_id = employee.department_id.manager_id
        if not self.filtered('department_id.manager_id'):
            self.parent_id = self.parent_id

    @api.depends('parent_id')
    def _compute_coach(self):
        for employee in self:
            manager = employee.parent_id
            previous_manager = employee._origin.parent_id
            if manager and (employee.coach_id == previous_manager or not employee.coach_id):
                employee.coach_id = manager
            elif not employee.coach_id:
                employee.coach_id = False

    coach_id = fields.Many2one(
        'hr.employee', 'Coach', compute='_compute_coach', store=True, readonly=False,
        domain="['|', ('company_id', '=', False),'|', '|',('allowed_companies', 'in', allowed_companies),('company_id', 'in', allowed_companies),'|', ('allowed_companies', 'in', company_id),('company_id', '=', company_id)]",
        help='Select the "Employee" who is the coach of this employee.\n'
             'The "Coach" has no specific rights or responsibilities by default.')

    @api.model
    def create(self, values):
        record = super(HrEmployee, self).create(values)
        if not record.address_home_id:
            record.address_home_id = record.env['res.partner'].sudo().create({'name': record.name,
                                                                              'email': record.work_email,
                                                                              'company_id': record.company_id.id,
                                                                              'company_type': 'person',
                                                                              'ref': record.zk_emp_id,
                                                                              'phone': record.phone_num,
                                                                              'mobile': record.work_phone or record.mobile_phone,
                                                                              'email': record.work_email ,
                                                                              'x_studio_arabic_name': record.employee_arabic_name ,
                                                                              'employee_database_id': record.id ,
                                                                              'employee_hire_date': record.hire_date ,
                                                                              'employee_resignation_date': record.resignation_date ,
                                                                              'employee_state': record.state ,
                                                                              'id_def': record.identification_id	 ,
                                                                              'street': record.address_home_id.street	 ,
                                                                              'from_hr': True,
                                                                              })


        return record


    def write(self, vals):
        old_zk_emp_id=self.zk_emp_id
        res = super(HrEmployee, self).write(vals)
        if 'company_id' in vals:
            if self.address_home_id:
                self.address_home_id.company_id = self.company_id.id
            if self.address_id:
                self.address_id.company_id = self.company_id.id
            contracts = self.env['hr.contract'].sudo().search([('employee_id', '=', self.id)])
            for rec in contracts:
                rec.company_id = self.company_id.id
        if 'allowed_companies' in vals:
            if self.address_home_id:
                self.address_home_id.allowed_companies = [(6, 0, self.allowed_companies.ids)]
            if self.address_id:
                self.address_id.allowed_companies = [(6, 0, self.allowed_companies.ids)]

        record=self.env['res.partner'].sudo().search([('ref','=',old_zk_emp_id)]).write({'name': self.name,
                                                 'ref': self.zk_emp_id,
                                                 'email': self.work_email,
                                                 'company_id': self.company_id.id,
                                                 'company_type': 'person',
                                                 'ref': self.zk_emp_id,
                                                 'phone': self.phone_num,
                                                 'mobile': self.work_phone or self.mobile_phone,
                                                 'email': self.work_email,
                                                 'x_studio_arabic_name': self.employee_arabic_name,
                                                 'employee_database_id': self.id,
                                                 'employee_hire_date': self.hire_date,
                                                 'employee_resignation_date': self.resignation_date,
                                                 'employee_state': self.state,
                                                 'id_def': self.identification_id	,
                                                 'street': self.address_home_id.street	 ,
                                                 'from_hr': True,
                                                 })
        return res
