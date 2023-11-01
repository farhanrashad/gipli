# -*- coding: utf-8 -*-

from babel.dates import format_date
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
        
class Exam(models.Model):
    _name = 'oe.exam'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Exam'
    _rec_name = 'subject_id'

    READONLY_STATES = {
        'schedule': [('readonly', True)],
        'complete': [('readonly', True)],
        'prepare': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    
    exam_session_id = fields.Many2one(
        comodel_name='oe.exam.session',
        string="Exam Session", states=READONLY_STATES,
        required=True, ondelete='cascade', index=True, copy=False)

    batch_id = fields.Many2one(
        comodel_name='oe.school.course.batch',
        string="Batch", required=True,
        states=READONLY_STATES,
        change_default=True, ondelete='restrict', )
    
    subject_id = fields.Many2one(
        comodel_name='oe.school.course.subject',
        string="Subject", required=True, states=READONLY_STATES,
        change_default=True, ondelete='restrict', )
    marks_min = fields.Float(string='Minimum Marks', required=True, states=READONLY_STATES,)
    marks_max = fields.Float(string='Maximum Marks', required=True, states=READONLY_STATES,)
    date_start = fields.Datetime(string='Start Time', required=True, states=READONLY_STATES,)
    date_end = fields.Datetime(string='End Time', required=True, states=READONLY_STATES,)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('schedule', 'Scheduled'),
        ('complete', 'Completed'),
        ('prepare', 'Result Prepared'),
        ('done', 'Result Updated'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        states=READONLY_STATES,
        default=lambda self: self.env.company)
    # Address Fields
    address_id = fields.Many2one('res.partner', 'Work Address', 
                                 compute="_compute_address_id", 
                                 store=True, readonly=False, states=READONLY_STATES,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    exam_location_id = fields.Many2one('oe.school.building.room', 'Exam Location', 
                                       compute="_compute_exam_location_id", 
                                       states=READONLY_STATES,
                                       store=True, readonly=False,
                                       domain="[('building_id.address_id', '=', address_id)]")

    exam_hours = fields.Float(string='Exam Hours', 
                              compute='_compute_exam_hours', 
                              store=True, readonly=True)

    exam_result_line = fields.One2many('oe.exam.result', 'exam_id', string='Exams', states=READONLY_STATES,)
    exam_result_count = fields.Integer('Exam Result Count', compute='_compute_exam_result')
    
    # ----------------------------------------
    # Compute Methods
    # ----------------------------------------
    
    @api.depends('company_id')
    def _compute_address_id(self):
        for exam in self:
            address = exam.company_id.partner_id.address_get(['default'])
            exam.address_id = address['default'] if address else False

    @api.depends('address_id')
    def _compute_exam_location_id(self):
        to_reset = self.filtered(lambda e: e.address_id != e.exam_location_id.building_id.address_id)
        to_reset.exam_location_id = False

    @api.depends('date_start', 'date_end')
    def _compute_exam_hours(self):
        for exam in self:
            if exam.date_start and exam.date_end:
                delta = exam.date_end - exam.date_start
                exam.exam_hours = delta.total_seconds() / 3600.0
            else:
                exam.exam_hours = False

    def _compute_exam_result(self):
        for record in self:
            record.exam_result_count = len(record.exam_result_line)
            
    # CRUD Operations
    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError("You cannot delete a record with applicants when the status is not 'Draft'.")
        return super(Exam, self).unlink()

    @api.constrains('exam_hours')
    def _check_exam_hours(self):
        for record in self:
            if record.exam_hours < 0:
                raise ValidationError("The End date cannot be less than start date.")

    
    # Action Buttons
    def button_draft(self):
        self.write({'state': 'draft'})

    def button_schedule(self):
        self.write({'state': 'schedule'})

    def button_close(self):
        self.write({'state': 'complete'})
        
    def button_cancel(self):
        self.write({'state': 'draft'})

    def button_prepare_result(self):
        student_ids = self.env['res.partner'].search([('course_id','=',self.exam_session_id.course_id.id),('batch_id','=',self.batch_id.id)])
        #raise UserError(student_ids)
        for student in student_ids:
            exam_result = self.env['oe.exam.result'].create({
                'student_id': student.id,
                'exam_id': self.id,
                'attendance_status': 'present',
                'marks': 0,
            })
        self.write({'state': 'prepare'})

    def button_complete_result(self):
        for exam in self:
            if any(er.marks == 0 for er in exam.exam_result_line.filtered(lambda e: e.attendance_status == 'present')):
                raise UserError("One or more student's marks are not updated.")
        self.write({'state': 'done'})

    def action_view_exam_results(self):
        context = {
            'default_exam_id': self.id,
            'exam_id': self.id,
        }
        action = {
            'name': 'Exam Result',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'oe.exam.result',
            'type': 'ir.actions.act_window',
            'context': context,
        }
        return action
    
    def button_open_result(self):
        context = {
            'default_exam_id': self.id,
            'exam_id': self.id,
            'create': False,
            'delete': False,
        }
        action = {
            'name': 'Exam Result',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'oe.exam.result',
            'type': 'ir.actions.act_window',
            'context': context,
        }
        return action