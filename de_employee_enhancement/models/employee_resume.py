# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class HrResumeLineInh(models.Model):
    _inherit = 'hr.resume.line'

    institute = fields.Char('Institute')
    reason_to_leave = fields.Char('Reason To Leave')
    salary = fields.Float('Salary')
    cgpa = fields.Char('Division/CGPA')
    is_experience = fields.Boolean('Is Experience?', default=False)
    is_education = fields.Boolean('Is Education?', default=False)

    @api.onchange('line_type_id')
    def compute_experience(self):
        if self.line_type_id.name == 'Experience':
            self.is_experience = True
            self.is_education = False
        if self.line_type_id.name == 'Education':
            self.is_education = True
            self.is_experience = False
            print(self.line_type_id.name)

