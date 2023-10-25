# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_student_attendance_use_pin = fields.Boolean(
        string='Student PIN',
        implied_group="de_school_attendance.group_student_attendance_use_pin")

    student_attendance_mode = fields.Selection(related='company_id.student_attendance_mode', readonly=False)
    student_attendance_with_time = fields.Boolean(related='company_id.student_attendance_with_time', readonly=False)
    
    attendance_kiosk_mode = fields.Selection(related='company_id.student_attendance_kiosk_mode', readonly=False)
    attendance_barcode_source = fields.Selection(related='company_id.student_attendance_barcode_source', readonly=False)
    attendance_kiosk_delay = fields.Integer(related='company_id.student_attendance_kiosk_delay', readonly=False)
