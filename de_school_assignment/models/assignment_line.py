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
        index=True,
        auto_join=True,
        ondelete="cascade",
        domain="[('state','=','publish')]"
    )
    date_due = fields.Datetime(related='assignment_id.date_due')
    course_id = fields.Many2one('oe.school.course',related='assignment_id.course_id')
    subject_id = fields.Many2one('oe.school.subject',related='assignment_id.subject_id')
    
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
        ('submitted', 'Submitted'),
        ('expired', 'Expired'),
        ('cancel', 'Cancelled'),
    ], string='Assignment Status', default='draft')

    date = fields.Datetime(string='Date Submission', readonly=True)

    # CRUD Operations
    def write1111(self, vals):
        res = super(AssignmentSubmit, self).write(vals)
        if 'file_submit' in vals and vals['file_submit']:
            body = 'Assignment submitted by ' + self.student_id.name
            attachment = self.env['ir.attachment'].create(
                self._assignment_values('oe.assignment',self.assignment_id.id,vals['file_submit'])
            )
            self.assignment_id.message_post(body=body, attachment_ids=[attachment.id])
            #self.message_post(body=body, attachment_ids=[attachment.id])
        return res

    
        
    # Action Buttons
    def button_draft(self):
        self.write({'state': 'draft'})

    def button_submit(self):
        self._action_submit()
        self.write({
            'state': 'submitted',
            'date': datetime.now(),
        })

    def _action_submit(self):
        body = 'Assignment submitted by ' + self.student_id.name
        attachment = self.env['ir.attachment'].create(
            self._assignment_values('oe.assignment',self.assignment_id.id,self.file_submit)
        )
        self.assignment_id.message_post(body=body, attachment_ids=[attachment.id])
        
    def _assignment_values(self, res_model, res_id, file):
        student = self.student_id.roll_no if self.student_id.roll_no else self.student_id.name
        vals = {
            'name': self.assignment_id.name + '_' + student,
            'datas': file,
            'res_model': res_model,
            'res_id': res_id,
        }
        return vals
    def button_cancel(self):
        self.write({'state': 'draft'})
        