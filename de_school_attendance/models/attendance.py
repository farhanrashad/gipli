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
    _description = "Attendance"
    _order = "check_in desc"

    def _default_student(self):
        return self.env.user.partner_id

    student_id = fields.Many2one('res.partner', string="Student", 
                                 default=_default_student, 
                                 domain="[('is_student','=',True)]",
                                 required=True, ondelete='cascade', index=True)
    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now)
    check_out = fields.Datetime(string="Check Out")
    attendance_hours = fields.Float(string='Attendance Hours', compute='_compute_attendance_hours', store=True, readonly=True)

    attendance_type = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
    ], string='Attendance Mode', default='present')
    is_late_arrival = fields.Boolean(string='Late Arrival')
    attendance_sheet_id = fields.Many2one('oe.attendance.sheet', string='Attendance Sheet')
    # Compute Methods
    @api.depends('check_in', 'check_out')
    def _compute_attendance_hours(self):
        for attendance in self:
            if attendance.check_out and attendance.check_in:
                delta = attendance.check_out - attendance.check_in
                attendance.attendance_hours = delta.total_seconds() / 3600.0
            else:
                attendance.attendance_hours = False