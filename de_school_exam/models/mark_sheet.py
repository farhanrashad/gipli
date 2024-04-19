# -*- coding: utf-8 -*-

from babel.dates import format_date
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


class MarkSheet(models.Model):
    _name = 'oe.exam.marksheet'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Mark Sheet'
    _rec_name = 'student_id'
    
    exam_session_id = fields.Many2one(
        comodel_name='oe.exam.session',
        string="Exam Session", 
        required=True, ondelete='cascade', index=True, copy=False,
        domain="[('state','=','progress')]"
    )
    student_id = fields.Many2one(
        comodel_name='res.partner',
        domain="[('is_student','=',True)]",
        string="Student", required=True, 
        change_default=True, ondelete='restrict', 
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Generated'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
    company_id = fields.Many2one(related='exam_session_id.company_id')

    dynamic_view_arch = fields.Html(compute='_compute_dynamic_view_arch')
    
    marksheet_line = fields.One2many('oe.exam.marksheet.line', 'marksheet_id', string='Mark Sheet', )
    
    # Constrains
    @api.constrains('exam_session_id', 'student_id', 'state')
    def _check_unique_marksheet(self):
        domain = [
                ('exam_session_id', '=', self.exam_session_id.id),
                ('student_id', '=', self.student_id.id),
                ('state', '=', ['draft','done']),
                ('id', '!=', self.id),  # Exclude current record
        ]
        if self.search_count(domain) > 0:
            raise exceptions.ValidationError(_('Mark Sheet must be unique per session for a student.'))

    @api.depends('marksheet_line')
    def _compute_dynamic_view_arch(self):
        for marks in self:
            # Prepare dynamic fields based on the number of records in group_line_ids
            dynamic_fields = [
                f'<field name="dynamic_field_{index}" string="Dynamic Field {index}" />' 
                for index in range(1, len(marks.marksheet_line) + 1)
            ]

            # Construct the dynamic arch
            dynamic_arch = f'<form><sheet><notebook><page>{"".join(dynamic_fields)}</page></notebook></sheet></form>'
            marks.dynamic_view_arch = dynamic_arch

    
    # Actions
    def button_draft(self):
        pass

    def button_generate(self):
        exam_ids = self.env['oe.exam'].search([
            ('exam_session_id','=',self.exam_session_id.id)
        ])
        subject_ids = exam_ids.mapped('subject_id')
        for subject in subject_ids:
            self.marksheet_line.create({
                'subject_id': subject.id,
                'marksheet_id': self.id,
            })

    def button_cancel(self):
        pass

class MarkSheetLine(models.Model):
    _name = 'oe.exam.marksheet.line'
    _description = 'Marksheet Line'

    marksheet_id = fields.Many2one(
        comodel_name='oe.exam.marksheet',
        string="Mark Sheet", 
        required=True, ondelete='cascade', index=True, copy=False)
    subject_id = fields.Many2one('oe.school.subject', string='Subject',
                                 domain="[('id','in',subject_ids)]",
                                 required=True,
                                )
    

    