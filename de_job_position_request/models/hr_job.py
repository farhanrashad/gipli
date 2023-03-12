# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.exceptions import Warning


class HrJob(models.Model):
    _inherit = 'hr.job'

    hired_employees = fields.Integer('Hired Employees', compute='_compute_hired_employees')
    required_employees = fields.Integer('Required Employees', compute='_compute_hired_employees')
    
    def _compute_hired_employees(self):
        for job in self:
            job.hired_employees = len(job.application_ids.filtered(lambda line: line.stage_id.hired_stage))
            job.required_employees = 1
    