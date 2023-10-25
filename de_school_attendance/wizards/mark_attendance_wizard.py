# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AttendanceMarkWizard(models.TransientModel):
    _name = 'oe.attendance.mark.wizard'
    _description = 'Mark Student Attendance'

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, index=True, readonly=False)

    attendance_sheet_id = fields.Many2one('oe.attendance.sheet',string="Attendance Sheet", readonly=True )
    mode_attendance = fields.Selection([
        ('absent', 'Mark Absent'),
        ('present', 'Mark Present'),
        ('late', 'Mark Late Arrivals'),
    ], string='Attendance Mode', default='absent', required=True)

    student_ids = fields.Many2many('res.partner',
        relation='oe_attendance_mark_wizard_students_rel',
        column1='wizard_id',
        column2='student_id',
        string='Students'
    )

    
    @api.model
    def default_get(self, fields):
        res = super(AttendanceMarkWizard, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id', [])
        record = self.env[active_model].search([('id','=',active_id)])
        #raise UserError(record.name)
        res['attendance_sheet_id'] = record.id
        #self.attendance_sheet_id = record.id
        return res

    
    def _compute_from_attedance_register(self):
        for record in self:
            record.course_id = record.attendance_register_id.course_id.id

    
    def action_process_attendance(self):
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])
        record_ids = self.env[active_model].search([('id','in',active_ids)])
        
    