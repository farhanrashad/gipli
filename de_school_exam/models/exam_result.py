# -*- coding: utf-8 -*-

from babel.dates import format_date
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
        
class ExamResult(models.Model):
    _name = 'oe.exam.result'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Exam Results'
    _rec_name = 'student_id'

    READONLY_STATES = {
        'progress': [('readonly', True)],
        'close': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    
    exam_id = fields.Many2one(
        comodel_name='oe.exam',
        string="Exam", states=READONLY_STATES,
        required=True, ondelete='cascade', index=True, copy=False)

    batch_id = fields.Many2one(
        comodel_name='oe.school.course.batch',
        related='exam_id.batch_id'
    )
    
    subject_id = fields.Many2one(
        comodel_name='oe.school.course.subject',
        related='exam_id.subject_id',
    )

    student_id = fields.Many2one(
        comodel_name='res.partner',
        domain="[('is_student','=',True),('batch_id','=',batch_id)]",
        string="Student", required=True, states=READONLY_STATES,
        change_default=True, ondelete='restrict', 
    )
    roll_no = fields.Char(related='student_id.roll_no')
    admission_no = fields.Char(related='student_id.admission_no')
    
    attendance_status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
    ], string='Attendance Type', default='present', required=True)
    seat_no = fields.Char('Seat No')
    marks = fields.Float(string='Obtained Marks', required=True, states=READONLY_STATES,)
    credit_points = fields.Float(string='Credit Points')
    exam_grade_line_id = fields.Many2one('oe.exam.grade.line', string='Exam Grade', compute='_compute_exam_grade')
    
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        states=READONLY_STATES,
        default=lambda self: self.env.company)
    
    # ----------------------------------------
    # Constrains
    # ----------------------------------------

    @api.constrains('marks')
    def _check_marks_range(self):
        for record in self:
            if record.marks < record.exam_id.marks_min or record.marks > record.exam_id.marks_max:
                raise ValidationError(f"Obtained Marks must be between {record.exam_id.marks_min} and {record.exam_id.marks_max}.")


            
    # CRUD Operations
    def unlink11(self):
        for record in self:
            if record.exam_id.state != 'draft':
                raise ValidationError("You cannot delete result.")
        return super(ExamResult, self).unlink()

    #compute Methods
    @api.depends('marks')
    def _compute_exam_grade(self):
        for result in self:
            # Get the grade lines ordered by score_min in descending order
            grade_lines = self.env['oe.exam.grade.line'].search([('exam_grade_id','=',result.batch_id.exam_grade_id.id)], order='score_min DESC')

            # Find the first grade that the score is greater than or equal to
            for line in grade_lines:
                if result.marks >= line.score_min:
                    result.exam_grade_line_id = line.id
                    break

        
    