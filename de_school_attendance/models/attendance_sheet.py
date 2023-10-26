# -*- coding: utf-8 -*-

from babel.dates import format_date
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AttendanceSheet(models.Model):
    _name = "oe.attendance.sheet"
    _description = "Attendance Sheet"
    _order = "name asc"

    READONLY_STATES = {
        'progress': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    name = fields.Char(string='Name', required=True, index='trigram', translate=True,  states=READONLY_STATES,)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'Attendance Start'),
        ('done', 'Attendance Taken'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, states=READONLY_STATES,)
    date = fields.Date(string='Date', required=True, states=READONLY_STATES,)
    
    attendance_register_id = fields.Many2one('oe.attendance.register', string='Attendance Register', required=True, states=READONLY_STATES,)
    course_id = fields.Many2one('oe.school.course', related='attendance_register_id.course_id')
    batch_id = fields.Many2one('oe.school.course.batch', string='Batch', required=True, states=READONLY_STATES,)

    description = fields.Html(string='Description')

    sheet_to_close = fields.Boolean(string='Sheet to Close', compute='_compute_sheet_to_close')
    attendance_sheet_line = fields.One2many('oe.attendance.sheet.line', 'attendance_sheet_id', string='Sheet Lines')

    _sql_constraints = [
        ('unique_date_attendance_register', 'unique(date, attendance_register_id)', 
         'Attendance has already been marked for the given date.'
        ),
    ]

    @api.depends('state','attendance_sheet_line')
    def _compute_sheet_to_close(self):
        for record in self:
            if record.state == 'progress':
                if len(record.attendance_sheet_line) > 0:
                    record.sheet_to_close = True
                else:
                    record.sheet_to_close = False
            else:
                record.sheet_to_close = False
        
    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise exceptions.UserError("You cannot delete a record with the status is not 'Draft'.")
        return super(YourModel, self).unlink()

    def button_draft(self):
        self.write({'state': 'draft'})

    def button_open(self):
        self.write({'state': 'progress'})

    def button_close(self):
        self.write({'state': 'done'})
        
    def button_cancel(self):
        self.write({'state': 'draft'})

    def button_mark_attendance(self):
        self.ensure_one()
        #raise UserError(self.id)
        
        action = {
            'name': _('Mark Attendance'),
            'res_model': 'oe.attendance.mark.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'oe.attendance.sheet',
                'active_ids': self.ids,
                'active_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
        return action

class AttendanceSheet(models.Model):
    _name = "oe.attendance.sheet.line"
    _description = "Attendance Sheet Line"
    _order = "student_id asc"

    attendance_sheet_id = fields.Many2one('oe.attendance.sheet', string='Attendance Sheet')
    student_id = fields.Many2one('res.partner', string="Student", 
                                 domain="[('is_student','=',True)]",
                                 required=True, ondelete='cascade', index=True)
    attendance_mode = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ], string='Attendance Mode', default='present')
                                 
    