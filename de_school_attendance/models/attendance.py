# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import datetime, timedelta
from operator import itemgetter

import pytz
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
from odoo.osv.expression import AND, OR
from odoo.tools.float_utils import float_is_zero
from odoo.exceptions import AccessError


class StudentAttendance(models.Model):
    _name = "oe.student.attendance"
    _description = "Student Attendance"
    _order = "check_in desc"


    student_id = fields.Many2one('res.partner', string="Student", 
                                 domain="[('is_student','=',True)]",
                                 required=True, ondelete='cascade', index=True)
    date_attendance = fields.Date('Attendance Date', required=True)
    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now)
    check_out = fields.Datetime(string="Check Out")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    student_attendance_mode = fields.Selection(related='company_id.student_attendance_mode')

    attendance_hours = fields.Float(string='Attendance Hours', compute='_compute_attendance_hours', store=True, readonly=True)

    attendance_status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
    ], string='Attendance Type', default='present')
    is_late_arrival = fields.Boolean(string='Late Arrival')
    attendance_sheet_id = fields.Many2one('oe.attendance.sheet', string='Attendance Sheet')

    # ----------------------------------------
    # Constraints
    # ----------------------------------------
    @api.constrains('student_id', 'date_attendance')
    def _check_student_attendance_overlap(self):
        for record in self:
            if record.student_attendance_mode == 'period':
                # Check if there are any overlapping records with the same student and date_attendance
                domain = [
                    ('student_id', '=', record.student_id.id),
                    ('date_attendance', '=', record.date_attendance),
                    ('id', '!=', record.id),
                    '|',
                    ('check_in', '<=', record.check_in),
                    ('check_out', '>=', record.check_in),
                ]
            else:
                # Check if there are any overlapping records with the same student and date_attendance
                domain = [
                    ('student_id', '=', record.student_id.id),
                    ('date_attendance', '=', record.date_attendance),
                    ('id', '!=', record.id),
                ]
            
            if self.search_count(domain) > 0:
                raise exceptions.ValidationError(_('Student attendance cannot overlap.'))

    # ----------------------------------------
    # Compute Methods
    # ----------------------------------------
    @api.depends('check_in', 'check_out')
    def _compute_attendance_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                delta = attendance.check_out - attendance.check_in
                attendance.attendance_hours = delta.total_seconds() / 3600.0
            else:
                attendance.attendance_hours = False