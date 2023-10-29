# -*- coding: utf-8 -*-

from babel.dates import format_date
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ExamSession(models.Model):
    _name = 'oe.exam.session'
    _description = 'Exam Session'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = "name asc"

    READONLY_STATES = {
        'progress': [('readonly', True)],
        'close': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    
    name = fields.Char(string='Name', required=True)
    marks_min = fields.Float(string='Minimum Marks', required=True)
    marks_max = fields.Float(string='Maximum Marks', required=True)
    course_id = fields.Many2one(
        comodel_name='oe.school.course',
        string="Course",
        change_default=True, ondelete='restrict', )
    exam_type_id = fields.Many2one('oe.exam.type', string='Exam Type', required=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'Open'),
        ('close', 'Closed'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    

    exam_line = fields.One2many('oe.exam', 'exam_session_id', string='Exams')
    exam_count = fields.Integer('Exam Count', default='_compute_exam')

    # Compute Methods
    def _compute_exam(self):
        for record in self:
            record.exam_count = len(record.exam_line)
            
    # CRUD Operations
    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise exceptions.UserError("You cannot delete a record with applicants when the status is not 'Draft'.")
        return super(ExamSession, self).unlink()

    # Action Buttons
    def button_draft(self):
        self.write({'state': 'draft'})
        return {}

    def button_open(self):
        self.write({'state': 'progress'})
        return {}

    def button_close(self):
        self.write({'state': 'close'})
        return {}
        
    def button_cancel(self):
        self.write({'state': 'draft'})
        return {}

    

