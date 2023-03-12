# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.exceptions import Warning
from odoo import exceptions


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    skill_id = fields.One2many('employee.hr.skill',  'applicant_id', string='Skills')
    
    def create_employee_from_applicant(self):
        res = super(HrApplicant, self).create_employee_from_applicant()
        if self.job_id.remaining_id == 0:
            raise exceptions.ValidationError('The Desired Number of Employee already Hired')
        return res


class HrSkill(models.Model):
    _name = 'employee.hr.skill'
    _description = 'This is skill set'

    pref_name = fields.Char('Name', required=True)
    pref_value = fields.Char('Skill')
    skill_level = fields.Char(string='Level')
    applicant_id = fields.Many2one('hr.applicant', string='Applicant')

