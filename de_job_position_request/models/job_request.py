# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero
from datetime import datetime


JOB_POSITION_REQUEST_STATES = [
    ('draft', 'Draft'),
    ('pending', 'Waiting for Approval'),
    ('confirm', 'confirmed'),
    ('done', 'Done'),
    ('cancel', 'Cancelled')
]

class JobPositionRequestType(models.Model):
    _name = 'hr.job.position.request.type'
    _description = 'Job Position Request Type'

    name = fields.Char(string='Name', required=True, translate=True)
    sequence = fields.Integer(default=1)
    request_type = fields.Selection([
        ('budget', 'Budgeted Positions'),
        ('nonbudget', 'Non-Budgeted'),
    ], default="budget", required=True, string='Request Type')
    position_type = fields.Selection([('new', 'For New Position'),
                             ('old', 'For Old Job ')], default='new', string='Position Type', required=True)
   
class JobPositionRequest(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _name = 'hr.job.position.request'
    _description = 'Job Position Request'
    
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))

    position_request_type_id = fields.Many2one('hr.job.position.request.type', string='Position Request Type', required=True)
    request_type = fields.Selection(related='position_request_type_id.request_type', readonly=True)
    position_type = fields.Selection(related='position_request_type_id.position_type', readonly=True)

    date_request = fields.Date(string='Request On', required=True, default=datetime.today())
    date_planned = fields.Date(string='Planned Date', required=True, default=datetime.today())
    
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_from_job_id', store=True)
    manager_id = fields.Many2one('hr.employee', compute='_compute_from_department_id', store=True, readonly=False, copy=False, string='Manager')
    user_id = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, check_company=True)
    company_id = fields.Many2one('res.company','Company',default=lambda self:self.env.company.id, required=True, copy=True)
    
    job_id = fields.Many2one('hr.job', string='Job Position', help='if position type is old')
    no_of_recruitment = fields.Integer(string='Expected New Employees', default=1, required=True)
    no_of_employee = fields.Integer(related='job_id.no_of_employee')
    expected_employees = fields.Integer(related='job_id.expected_employees')
    no_of_hired_employee = fields.Integer(related='job_id.no_of_hired_employee')
    
    state = fields.Selection(JOB_POSITION_REQUEST_STATES,
                              'Status', tracking=True, required=True,
                              copy=False, default='draft')

    
    active = fields.Boolean("Active", default=True, help="If the active field is set to false, it will allow you to hide the case without removing it.")
    
    
    date_submit = fields.Datetime('Submission Date', readonly=True)
    date_approved = fields.Datetime('Submission Date', readonly=True)    
    
    description = fields.Text("Requirements", help="Job position requirements", translate=True)        
    
    @api.depends('job_id')
    def _compute_from_job_id(self):
        for request in self:
            request.department_id = request.job_id.department_id.id
            
    @api.depends('department_id')
    def _compute_from_department_id(self):
        for request in self:
            request.manager_id = request.department_id.manager_id.id
    
    @api.depends('company_id')
    def _compute_employee_id(self):
        if not self.env.context.get('default_employee_id'):
            for course in self:
                course.employee_id = self.env.user.with_company(course.company_id).employee_id
    
    
    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('job.position.request') or _('New')

        result = super(JobPositionRequest, self).create(vals)
        return result
    
    def _prepare_job(self):
        vals = {}
        job = self.env['hr.job']
        vals = {
            'name': self.job_id.name,
            'description': self.description,
            'company_id': self.company_id.id,
            'address_id': self.company_id.partner_id.id,
            'department_id': self.department_id.id,
            'manager_id': self.manager_id.id,
            'user_id': self.user_id.id,
            'hr_responsible_id': self.user_id.id,
            'no_of_recruitment': self.no_of_recruitment,
            }
        if self.position_type == 'new':
            job = self.env['hr.job'].create(vals)
            self.job_id = job.id
        else:
            self.job_id.write({
                'no_of_recruitment': self.job_id.no_of_recruitment + self.no_of_recruitment,
            })
        
        
    def button_submit(self):
        for request in self:
            #if request.request_type == 'budget':
            #    self._prepare_job()
            self.update({
                'date_submit' : fields.Datetime.now(),
                'state' : 'pending',
            })
        
    def button_confirm(self):
        for request in self.sudo():
            if not self.user_has_groups('de_job_position_request.group_hr_recruitment_approver'):
                    raise UserError(_("You are not authorized to approve request"))
            
            self._prepare_job()
            self.update({
                'date_approved' : fields.Datetime.now(),
                'state' : 'confirm',
            })
            
    def button_close(self):
        for request in self.sudo():
            if not self.user_has_groups('de_job_position_request.group_hr_recruitment_approver'):
                    raise UserError(_("You are not authorized to approve request"))
            
            self._prepare_job()
            self.update({
                'date_approved' : fields.Datetime.now(),
                'state' : 'done',
            })
            
    def button_refuse(self):
        for request in self.sudo():
            if not self.user_has_groups('de_job_position_request.group_hr_recruitment_approver'):
                    raise UserError(_("You are not authorized to refuse request"))
                
        if job.stage_id.prv_stage_id:
            job.update({
                'stage_id' : job.stage_id.prv_stage_id.id,
            })

    def button_cancel(self):
        self.update({
            'state': 'cancel',
        })

    def _track_template(self, changes):
        res = super(JobPositionRequest, self)._track_template(changes)
        job_request = self[0]
        if 'stage_id' in changes and job_request.stage_id.mail_template_id:
            res['stage_id'] = (job_request.stage_id.mail_template_id, {
                'auto_delete_message': True,
                'subtype_id': self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
                'email_layout_xmlid': 'mail.mail_notification_light'
            })
        return res