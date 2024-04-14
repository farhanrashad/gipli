# -*- coding: utf-8 -*-

import requests
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta, time
from dateutil.relativedelta import relativedelta
class TimetableWizard(models.TransientModel):
    _name = "oe.school.timetable.wizard"
    _description = 'Timetable Wizard'

    dayofweek = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
        ], 'Day of Week', required=True, default='0')
    
    course_id = fields.Many2one('oe.school.course', 'Course', store=True, required=True)
    
    use_batch = fields.Boolean(compute='_compute_batch_from_course')
    batch_id = fields.Many2one('oe.school.course.batch', 'Batch', store=True)
    use_section = fields.Boolean(compute='_compute_section_from_company')
    section_id = fields.Many2one('oe.school.course.section', 'Section',)
    
    subject_id = fields.Many2one('oe.school.subject', 'Subject', store=True, required=True)
    teacher_id = fields.Many2one('hr.employee', 'Teacher', store=True, domain="[('is_teacher','=',True)]")
    user_id = fields.Many2one('res.users',compute='_compute_user_from_teacher', store=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    calendar_id = fields.Many2one('resource.calendar', related='company_id.resource_calendar_id')
    classroom_id = fields.Many2one('oe.school.building.room', 'Classroom', store=True,)
    
    date_start = fields.Date("Start Date", compute='_compute_datetime', store=True, readonly=False, required=True, copy=True)
    date_end = fields.Date("End Date", compute='_compute_datetime', store=True, readonly=False, required=True, copy=True)

    hour_from = fields.Float(string='From', required=True)
    hour_to  = fields.Float(string='To', required=True)

    repeat_interval = fields.Integer("Repeat Every", default=1, )
    repeat_type = fields.Selection(
        [
            ('month', 'Month(s)'),
            ('week', 'Week(s)'),
            ('day', 'Day(s)'),
        ],
        string="Repeat Type", required=True, default='week',
        help="Repeat type determines how often a course timetable schedule."
    )

    def _compute_batch_from_course(self):
        for record in self:
            if record.course_id.use_batch and len(record.course_id.batch_ids) > 0:
                record.use_batch = True
            else:
                record.use_batch = False

    def _compute_section_from_company(self):
        for record in self:
            record.use_section = record.course_id.company_id.use_section
            
    @api.depends('batch_id')
    def _compute_datetime(self):
        for record in self:
            record.date_start = record.batch_id.date_start
            record.date_end = record.batch_id.date_end
            
    def action_create_timetable(self):
        current_date = self.date_start
        end_date = self.date_end
    
        while current_date <= end_date:
            attendance_records = self._find_school_time(current_date)
            #raise UserError(attendance_records)
            if attendance_records:
                self._create_timetable_records(current_date)

    
            if self.repeat_type == 'day':
                current_date += timedelta(days=self.repeat_interval)
            elif self.repeat_type == 'week':
                current_date += timedelta(weeks=self.repeat_interval)
            elif self.repeat_type == 'month':
                # Adding 1 month to the current date
                year = current_date.year + (current_date.month // 12)
                month = (current_date.month % 12) + self.repeat_interval
                current_date = current_date.replace(year=year, month=month, day=1)
    
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'name': _('Timetable'),
            'res_model': 'oe.school.timetable',
            'view_id': self.env.ref('de_school_timetable.school_timetable_tree_view').id,  # Replace 'your_module' with your module's name
            #'context': {'create': False, 'edit': False},
        }
        return action

    def _find_school_time(self, current_date):
        attendance_records = self.env['resource.calendar.attendance'].search([
            ('dayofweek', '=', current_date.weekday()),
            ('hour_from', '>=', self.hour_from),
            ('hour_to', '<=', self.hour_to),
        ])
        return attendance_records

    def _create_timetable_records(self, current_date):
        """
        Create timetable records for the given day and time range.
        """
        self.env['oe.school.timetable'].create({
            'course_id': self.course_id.id,
            'batch_id': self.batch_id.id,
            'subject_id': self.subject_id.id,
            'teacher_id': self.teacher_id.id,
            'user_id': self.user_id.id,
            'classroom_id': self.classroom_id.id,
            'date': current_date,
            'hour_from': self.hour_from,
            'hour_to': self.hour_to,
        })
