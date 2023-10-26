# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_student_attendance_use_pin = fields.Boolean(
        string='Student PIN',
        implied_group="de_school_attendance.group_student_attendance_use_pin")

    group_student_attendance_use_day = fields.Boolean(
        string='Day Attendance',
        implied_group="de_school_attendance.group_student_attendance_use_day")
    group_student_attendance_use_period = fields.Boolean(
        string='Period Attendance',
        implied_group="de_school_attendance.group_student_attendance_use_period")
    
    student_attendance_mode = fields.Selection(related='company_id.student_attendance_mode', readonly=False)
    student_attendance_with_time = fields.Boolean(related='company_id.student_attendance_with_time', readonly=False)
    
    attendance_kiosk_mode = fields.Selection(related='company_id.student_attendance_kiosk_mode', readonly=False)
    attendance_barcode_source = fields.Selection(related='company_id.student_attendance_barcode_source', readonly=False)
    attendance_kiosk_delay = fields.Integer(related='company_id.student_attendance_kiosk_delay', readonly=False)

    #@api.depends('student_attendance_mode')
    def _compute_attendance_type(self):
        if self.student_attendance_mode == 'day':
            self.group_student_attendance_use_day = True
            self.group_student_attendance_use_period = False
        else:
            self.group_student_attendance_use_day = False
            self.group_student_attendance_use_period = True
            
    def set_values111(self):
        day_grp = self.env.ref('de_school_attendance.group_student_attendance_use_day')
        period_grp = self.env.ref('de_school_attendance.group_student_attendance_use_period')
        base_user = self.env.ref('base.group_user')
        base_user_implied_ids = base_user.implied_ids
        day_grp.write({'users': [(4, base_user.id)]})
        #self.group_student_attendance_use_day = True
        #self.group_student_attendance_use_period = True
        #if self.student_attendance_mode == 'day':
        #    self.group_student_attendance_use_day = True
        #    self.group_student_attendance_use_period = False
        #else:
        #    self.group_student_attendance_use_day = False
        #    self.group_student_attendance_use_period = True
            
    @api.onchange('student_attendance_mode')
    def _onchange_group_stock_multi_locations(self):
        self.group_student_attendance_use_day = False
        self.group_student_attendance_use_period = False
        
        if self.student_attendance_mode == 'day':
            self.group_student_attendance_use_day = True
        else:
            self.group_student_attendance_use_period = True