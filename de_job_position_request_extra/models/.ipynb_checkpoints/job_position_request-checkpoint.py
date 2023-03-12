# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero
from datetime import datetime

   
class JobPositionRequest(models.Model):
    _inherit = 'hr.job.position.request'
    
    # Job Position Related Extra fields
    work_location = fields.Char('Work Location')
    job_function = fields.Char('Job Function')
    job_grade = fields.Char('Grade')
    employment_type = fields.Selection([
        ('regular', 'Regular'),
        ('contract_one', 'One Year Contract'),
    ], default="regular", string='Employement Type')
    
    file_jd = fields.Many2one('ir.attachment', string='JD Attachment')
    # Approval Fields
    approval_ceo = fields.Boolean(string='CEO Approval', compute='_compute_ceo_approval', store=True)
    approval_chairman = fields.Boolean(string='Chairman Approval')
    
    old_employee_name = fields.Char('Employee Name')
    old_job_title = fields.Char('Designation')
    old_position = fields.Char('Position')
    old_grade = fields.Char('Grade')
    
    old_employee_exit_reason = fields.Text('Employee Exit Reason')
    request_reason = fields.Text('Justification for Request')
    
    exp_essential = fields.Integer('Essential Exp.')
    exp_prefer = fields.Integer('Preferable Exp.')
    
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], default="male", string='Gender')
    
    exp_field = fields.Char('Field of Experience')
    min_edu = fields.Char('Minimum Qualification')
    min_tech_edu = fields.Char('Minimum Technical Qualification')
    com_lit_level = fields.Char('Compute Literacy Level')
    req_social = fields.Char('Social Requirements')
    
    @api.depends('request_type')
    def _compute_ceo_approval(self):
        for record in self:
            if record.request_type == 'nonbudget':
                record.approval_ceo = True