# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class AssignmentSubmit(models.Model):
    _name = 'oe.assignment.line'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Assignment Submission'
    _rec_name = 'student_id'
    _order = 'date desc, id desc'
    
    assignment_id = fields.Many2one(
        comodel_name='oe.assignment',
        string='Assignment',
        required=True,
        readonly=True,
        index=True,
        auto_join=True,
        ondelete="cascade",
        check_company=True,
    )
    date_due = fields.Datetime(related='assignment_id.date_due')
    course_id = fields.Many2one('oe.school.course',related='assignment_id.course_id')
    subject_id = fields.Many2one('oe.school.course.subject',related='assignment_id.subject_id')
    
    student_id = fields.Many2one(
        comodel_name='res.partner',
        domain="[('is_student','=',True)]",
        string="Student",
        change_default=True, ondelete='restrict')

    batch_id = fields.Many2one('oe.school.course.batch',related='student_id.batch_id')
    

    file_assignment = fields.Binary(related='assignment_id.file_assignment', string='Download Assignment')
    file_submit = fields.Binary(string='Submit Assignment', attachment=True)
    
    description = fields.Html(string='description')
    state = fields.Selection([
        ('draft', 'Pending'),
        ('submit', 'Submitted'),
        ('expire', 'Expired'),
        ('cancel', 'Cancelled'),
    ], string='Assignment Status', )

    date = fields.Datetime(string='Date Submission', readonly=True)

    # Action Buttons
    def button_draft(self):
        self.write({'state': 'draft'})

    def button_submit(self):
        self.write({
            'state': 'submit',
            'date': datetime.now(),
        })
        
    def button_cancel(self):
        self.write({'state': 'draft'})