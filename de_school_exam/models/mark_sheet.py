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

    marksheet_group_id = fields.Many2one(
        comodel_name='oe.exam.msheet.group',
        string="Marksheet Group", required=True,  
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Generated'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
    company_id = fields.Many2one(related='exam_session_id.company_id')
    
    marksheet_line = fields.One2many('oe.exam.marksheet.line', 'marksheet_id', string='Mark Sheet', )
    dynamic_view_arch = fields.Html(string='view code')
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

    

    
    # Actions
    def button_draft(self):
        pass

    def button_generate(self):
        self.marksheet_line.unlink()
        exam_ids = self.env['oe.exam'].search([
            ('exam_session_id','=',self.exam_session_id.id)
        ])
        subject_ids = exam_ids.mapped('subject_id')
        for subject in subject_ids:
            self.marksheet_line.create({
                'subject_id': subject.id,
                'marksheet_id': self.id,
            })

        self.dynamic_view_arch = self._compute_dynamic_view_arch()

    def button_cancel(self):
        pass

    def _compute_dynamic_view_arch(self):
        arch = ''
        for marks in self:
            # Prepare dynamic fields based on the number of records in group_line_ids
            dynamic_fields = [
                f'<field name="dynamic_field_{index}" string="Dynamic Field {index}" />' 
                for index in range(1, len(marks.marksheet_line) + 1)
            ]

            # Construct the dynamic arch
            arch += "<div class='o_field_widget o_field_section_and_note_one2many o_field_one2many'>"
            arch += "<div class='o_list_view o_field_x2many o_field_x2many_list'>"
            arch += "<div class='o_list_renderer o_renderer table-responsive o_list_renderer_2' style='position:absolute;top:0;left:0;'>"
            arch += "<table class='o_section_and_note_list_view o_list_table table table-sm table-hover position-relative mb-0 o_list_table_ungrouped table-striped' style='table-layout: fixed;'>"
            arch += "<thead>"
            arch += "<tr>"

            # field Labels
            arch += '<th data-tooltip-delay="1000" tabindex="2" data-name="subject_id" class="align-middle o_column_sortable position-relative cursor-pointer o_section_and_note_text_cell opacity-trigger-hover" style="width: 94px;">'
            arch += '<span class="d-block min-w-0 text-truncate flex-grow-1">'
            arch += 'Subject'
            arch += '</span>'
            arch += '</th>'
            for line in self.marksheet_group_id.ms_group_line:
                arch += '<th data-tooltip-delay="1000" tabindex="-1" data-name="name" class="aalign-middle o_column_sortable position-relative cursor-pointer o_list_number_th opacity-trigger-hover" style="min-width: 104px; width: 104px;">'
                arch += '<div class="d-flex flex-row-reverse">'
                arch += '<span class="d-block min-w-0 text-truncate flex-grow-1 o_list_number_th">'
                arch += line.exam_type_id.name
                arch += '</span>'
                arch += '</div>'
                arch += '</th>'

            arch += '<th data-tooltip-delay="1000" tabindex="-1" data-name="name" class="aalign-middle o_column_sortable position-relative cursor-pointer o_list_number_th opacity-trigger-hover" style="min-width: 104px; width: 104px;">'
            arch += '<div class="d-flex flex-row-reverse">'
            arch += '<span class="d-block min-w-0 text-truncate flex-grow-1 o_list_number_th">'
            arch += 'Total'
            arch += '</span>'
            arch += '</div>'
            arch += '</th>'
            
            arch += '</tr>'
            arch += '</thead>'
            arch += '<tbody>'

            for line in self.marksheet_line:
                arch += '<tr class="o_data_row o_is_false">'
                arch += '<td class="o_data_cell cursor-pointer o_field_cell o_list_text o_section_and_note_text_cell o_required_modifier">'
                arch += '<div class="o_field_widget o_required_modifier o_field_section_and_note_text o_field_text">'
                arch += line.subject_id.name
                arch += '</div>'
                arch += '</td>'
                
                for group in self.marksheet_group_id.ms_group_line:
                    arch += '<td class="o_data_cell cursor-pointer o_field_cell o_list_number o_readonly_modifier">'
                    arch += str(line._compute_marksheet_value())
                    arch += '</td>'

                arch += '<td class="o_data_cell cursor-pointer o_field_cell o_list_number o_readonly_modifier">'
                arch += '100'
                arch += '</td>'
                arch += '</tr>'
            arch += '</tbody>'
            arch += '</table>'
            arch += '</div>'
            arch += '</div>'
            arch += '</div>'
        return arch
            
class MarkSheetLine(models.Model):
    _name = 'oe.exam.marksheet.line'
    _description = 'Marksheet Line'

    marksheet_id = fields.Many2one(
        comodel_name='oe.exam.marksheet',
        string="Mark Sheet", 
        required=True, ondelete='cascade', index=True, copy=False)
    subject_id = fields.Many2one('oe.school.subject', string='Subject',
                                 required=True,
                                )

    def _compute_marksheet_value(self):
        val = self.subject_id.id
        return val

    