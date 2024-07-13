# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrContractInherit(models.Model):

    _inherit = 'hr.contract'

    zk_emp = fields.Char(string="Employee Attendance ID", compute='_get_attendance_id')

    def _get_attendance_id(self):
        for rec in self:
            rec.zk_emp = rec.employee_id.zk_emp_id




