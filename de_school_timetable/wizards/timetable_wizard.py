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

    course_id = fields.Many2one('oe.school.course', 'Course', store=True, required=True)
    batch_id = fields.Many2one('oe.school.course.batch', 'Batch', store=True, required=True)
    subject_id = fields.Many2one('oe.school.course.subject', 'Subject', store=True, required=True)
    teacher_id = fields.Many2one('hr.employee', 'Teacher', store=True, domain="[('is_teacher','=',True)]")
    user_id = fields.Many2one('res.users',compute='_compute_user_from_teacher', store=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    calendar_id = fields.Many2one('resource.calendar', related='company_id.resource_calendar_id')
    classroom_id = fields.Many2one('oe.school.building.room', 'Classroom', store=True,)
    
    date_start = fields.Date("Start Date", compute='_compute_datetime', store=True, readonly=False, required=True, copy=True)
    date_end = fields.Date("End Date", compute='_compute_datetime', store=True, readonly=False, required=True, copy=True)
    timetable_period_id = fields.Many2one('resource.calendar.attendance', string='Period', readonly=False, store=True, required=True, domain="[('calendar_id','=',calendar_id)]")

    repeat = fields.Boolean("Repeat", )
    repeat_interval = fields.Integer("Repeat every", default=1, )
    repeat_type = fields.Selection(
        [
            ('month', 'Month(s)'),
            ('week', 'Week(s)'),
            ('day', 'Day(s)'),
        ],
        string="Repeat Type", required=True, default='week',
        help="Repeat type determines how often a course timetable schedule."
    )

    @api.depends('batch_id')
    def _compute_datetime(self):
        for record in self:
            record.date_start = record.batch_id.date_start
            record.date_end = record.batch_id.date_end
            
    def action_create_timetable(self):
        current_date = self.date_start
        end_date = self.date_end
    
        while current_date <= end_date:
            self.env['oe.school.timetable'].create({
                'course_id': self.course_id.id,
                'batch_id': self.batch_id.id,
                'subject_id': self.subject_id.id,
                'teacher_id': self.teacher_id.id,
                'user_id': self.user_id.id,
                'classroom_id': self.classroom_id.id,
                'date': current_date,
                'timetable_period_id': self.timetable_period_id.id,
            })
    
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
            #'context': {'create': False, 'edit': False},
        }
        return action
