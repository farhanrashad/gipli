# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.osv.expression import OR


class ResCompany(models.Model):
    _inherit = 'res.company'

    student_attendance_mode = fields.Selection([
        ('day', 'By Day'),
        ('period', 'By Subject / Period'),
    ], string='Student Attendance Mode', default='day')
    student_attendance_with_time = fields.Boolean('Mark Attendance with Time')
    
    student_attendance_kiosk_mode = fields.Selection([
        ('barcode', 'Barcode / RFID'),
        ('barcode_manual', 'Barcode / RFID and Manual Selection'),
        ('manual', 'Manual Selection'),
    ], string='Student Attendance KIOSK Mode', default='barcode_manual')
    student_attendance_barcode_source = fields.Selection([
        ('scanner', 'Scanner'),
        ('front', 'Front Camera'),
        ('back', 'Back Camera'),
    ], string='Student Barcode Source', default='front')
    student_attendance_kiosk_delay = fields.Integer(default=10)


