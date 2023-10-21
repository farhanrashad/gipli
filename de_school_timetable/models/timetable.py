# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import date, datetime, timedelta, time
from dateutil.relativedelta import relativedelta
import json
import logging
import pytz
import uuid
from math import ceil, modf
    
class SchoolTimetable(models.Model):
    _name = 'oe.school.timetable'
    _description = 'School Timetable'
    _order = 'start_datetime,id desc'
    _rec_name = 'name'
    _check_company_auto = True
    
    name = fields.Text('Note', compute='_compute_name', store=True)
    course_id = fields.Many2one('oe.school.course', 'Course', store=True, required=True)
    batch_id = fields.Many2one('oe.school.course.batch', 'Batch', store=True, required=True)
    subject_id = fields.Many2one('oe.school.course.subject', 'Subject', store=True, required=True)
    teacher_id = fields.Many2one('hr.employee', 'Teacher', store=True, domain="[('is_teacher','=',True)]")
    user_id = fields.Many2one('res.users',compute='_compute_user_from_teacher', store=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    calendar_id = fields.Many2one('resource.calendar', related='company_id.resource_calendar_id')
    
    classroom_id = fields.Many2one('oe.school.building.room', 'Classroom', store=True,)
    date = fields.Date('Date')
    color = fields.Integer("Color", compute='_compute_color' )
    allocated_hours = fields.Float("Allocated Hours", compute='_compute_allocated_hours', store=True, readonly=False)
    allocated_percentage = fields.Float("Allocated Time (%)", default=100,
        compute='_compute_allocated_percentage', store=True, readonly=False,
        help="Percentage of time the employee is supposed to work during the shift.",
        group_operator="avg")
    
    state = fields.Selection([
            ('draft', 'Draft'),
            ('published', 'Published'),
    ], string='Status', default='draft')
    is_hatched = fields.Boolean(compute='_compute_is_hatched')
    timetable_period_id = fields.Many2one('resource.calendar.attendance', string='Period Templates', readonly=False, required=True, store=True, domain="[('calendar_id','=',calendar_id)]")
    
    repeat_interval = fields.Integer("Repeat every", default=1, required=True)
    repeat_type = fields.Selection(
        [
            ('month', 'Month(s)'),
            ('week', 'Week(s)'),
            ('day', 'Day(s)'),
        ],
        string="Repeat Type", required=True, default='week',
        help="Repeat type determines how often a course timetable schedule."
    )
    
    @api.constrains('course_id', 'batch_id', 'subject_id', 'timetable_period_id')
    def _check_duplicate_timetable(self):
        for record in self:
            domain = [
                ('course_id', '=', record.course_id.id),
                ('batch_id', '=', record.batch_id.id),
                ('subject_id', '=', record.subject_id.id),
                ('timetable_period_id', '=', record.timetable_period_id.id),
                ('date', '=', record.date),
            ]
            timetable_count = self.env['oe.school.timetable'].search_count(domain)
            #raise UserError(timetable_count)
            if timetable_count > 1:
                raise UserError("Timetable with the same Course, Batch, Subject, and Period already exists.")

    
    #@api.constrains('timetable_period_id', 'start_datetime')
    def _check_timetable_period(self):
        for record in self:
            timetables = self.filtered(lambda tt: tt.timetable_period_id and tt.start_datetime)
        if not timetables:
            return

        self.env["oe.school.timetable"].flush([
            "start_datetime", "timetable_period_id",
        ])
        
        # /!\ Computed stored fields are not yet inside the database.
        self._cr.execute('''
            SELECT tt2.id
            FROM oe_school_timetable tt
            JOIN resource_calendar_attendance period ON period.id = tt.timetable_period_id
            INNER JOIN oe_school_timetable tt2 ON
                tt2.start_datetime = tt.start_datetime
                AND tt2.timetable_period_id = period.id
                AND tt2.id != tt.id
            WHERE tt.id IN %s
        ''', [tuple(timetables.ids)])
        duplicated_tts = self.browse([r[0] for r in self._cr.fetchall()])
        #if duplicated_tts:
        #    raise ValidationError(_('Duplicated period detected. You probably encoded twice the same period:\n%s') % "\n".join(
         #       duplicated_tts.mapped(lambda m: "%(date_start)s" % {
         #           'date_start': m.start_datetime,
         #       })
         #   ))
            
    def _get_tz(self):
        return (self.env.user.tz
                or self._context.get('tz')
                or self.company_id.resource_calendar_id.tz
                or 'UTC')
    
    @api.depends('batch_id')
    def _compute_datetime(self):
        for record in self:
            record.start_datetime = record.batch_id.date_start
            record.end_datetime = record.batch_id.date_end
            
        #for tt in self.filtered(lambda s: s.timetable_period_id):
        #    tt.start_datetime, tt.end_datetime = self._calculate_start_end_dates(tt.start_datetime,
        #                                                                             tt.end_datetime,
        #                                                                             tt.timetable_period_id,
        #                                                                             )
    
    @api.model
    def _calculate_start_end_dates(self, start_datetime, end_datetime, timetable_period_id):
    
        def convert_datetime_timezone(dt, tz):
            return dt and pytz.utc.localize(dt).astimezone(tz)
    
        user_tz = pytz.timezone(self._get_tz())
    
        h = int(timetable_period_id.hour_from)
        m = round(modf(timetable_period_id.hour_from)[0] * 60.0)
        start = convert_datetime_timezone(start_datetime, pytz.timezone(self.env.user.tz or 'UTC'))
        start = start.replace(hour=int(h), minute=int(m))
        start = start.astimezone(pytz.utc).replace(tzinfo=None)
    
        h2 = int(timetable_period_id.hour_to)
        m2 = round(modf(timetable_period_id.hour_to)[0] * 60.0)
        end = convert_datetime_timezone(end_datetime, pytz.timezone(self.env.user.tz or 'UTC'))
        end = end.replace(hour=int(h2), minute=int(m2))
        end = end.astimezone(pytz.utc).replace(tzinfo=None)
    
        return (start, end)

    @api.depends('course_id','batch_id','subject_id','company_id')
    def _compute_name(self):
        for record in self:
            record.name = record.course_id.code + '/' + record.batch_id.name + ' - ' + record.subject_id.code
            
    @api.depends('course_id.color', 'subject_id.color')
    def _compute_color(self):
        for tt in self:
            tt.color = tt.subject_id.color or tt.course_id.color
            
    @api.depends('teacher_id')
    def _compute_user_from_teacher(self):
        for tt in self:
            tt.user_id = tt.teacher_id.user_id.id
            
    @api.depends('start_datetime', 'end_datetime', 'allocated_hours')
    def _compute_allocated_percentage(self):
        for tt in self:
            tt.allocated_percentage = 100
            
    @api.depends('state')
    def _compute_is_hatched(self):
        for tt in self:
            tt.is_hatched = tt.state == 'draft'


    
                
    # ----------------------------------------------------
    # Business Methods
    # ----------------------------------------------------
    def _add_delta_with_dst(self, start, delta):
        """
        Add to start, adjusting the hours if needed to account for a shift in the local timezone between the
        start date and the resulting date (typically, because of DST)

        :param start: origin date in UTC timezone, but without timezone info (a naive date)
        :return resulting date in the UTC timezone (a naive date)
        """
        try:
            tz = pytz.timezone(self._get_tz())
        except pytz.UnknownTimeZoneError:
            tz = pytz.UTC
        start = start.replace(tzinfo=pytz.utc).astimezone(tz).replace(tzinfo=None)
        result = start + delta
        return tz.localize(result).astimezone(pytz.utc).replace(tzinfo=None)
