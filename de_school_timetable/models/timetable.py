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
    _order = 'date,id desc'
    _rec_name = 'name'
    _check_company_auto = True
    
    name = fields.Text('Note', compute='_compute_name', store=True)
    course_ids = fields.Many2many(
        'oe.school.course', 'timetable_school_course_rel',
        string='Courses')
    course_id = fields.Many2one('oe.school.course', 'Course', store=True, required=True)
    batch_id = fields.Many2one('oe.school.course.batch', 'Batch', store=True, required=True)
    subject_id = fields.Many2one('oe.school.subject', 'Subject', store=True, required=True)
    teacher_id = fields.Many2one('hr.employee', 'Teacher', store=True, domain="[('is_teacher','=',True)]")
    user_id = fields.Many2one('res.users',compute='_compute_user_from_teacher', store=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    calendar_id = fields.Many2one('resource.calendar', related='company_id.resource_calendar_id')
    
    classroom_id = fields.Many2one('oe.school.building.room', 'Classroom', store=True,)
    date = fields.Date('Date', required=True)
    duration = fields.Float('Duration', 
                            #compute='_compute_duration', 
                            store=True, readonly=False)
    color = fields.Integer("Color", compute='_compute_color' )
    allday = fields.Boolean('All Day', default=False)
    state = fields.Selection([
            ('draft', 'Draft'),
            ('published', 'Published'),
    ], string='Status', default='draft')
    timetable_period_id = fields.Many2one('resource.calendar.attendance', string='Period Templates', readonly=False, required=True, store=True, domain="[('calendar_id','=',calendar_id)]")
    
    repeat_interval = fields.Integer("Repeat Every", default=1, required=True)
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
            ]
            if self.search_count(domain) > 1:
                raise UserError("Timetable with the same Course, Batch, Subject, and Period already exists.")

    
            
    def _get_tz(self):
        return (self.env.user.tz
                or self._context.get('tz')
                or self.company_id.resource_calendar_id.tz
                or 'UTC')

    @api.depends('course_id','batch_id','subject_id','company_id')
    def _compute_name(self):
        for record in self:
            record.name = str(record.course_id.code) + '/' + str(record.batch_id.name) + ' - ' + str(record.subject_id.code)
            
    @api.depends('course_id.color', 'subject_id.color')
    def _compute_color(self):
        for tt in self:
            tt.color = tt.subject_id.color or tt.course_id.color
            
    @api.depends('teacher_id')
    def _compute_user_from_teacher(self):
        for tt in self:
            tt.user_id = tt.teacher_id.user_id.id
                        
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

    # -----------------------------------
    # ----------- Actions ---------------
    # -----------------------------------
    def action_timetable_planning(self):
        action = self.env.ref('de_school_timetable.action_timetable_wizard').read()[0]
        action.update({
            'name': 'Timetable Planning',
            'res_model': 'oe.school.timetable.wizard',
            'type': 'ir.actions.act_window',
        })
        return action
        