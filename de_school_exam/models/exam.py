# -*- coding: utf-8 -*-

from babel.dates import format_date
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from lxml import etree
import xml.etree.ElementTree as ET

class Exam(models.Model):
    _name = 'oe.exam'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Exam'
    _rec_name = 'subject_id'

    READONLY_STATES = {
        'schedule': [('readonly', True)],
        'complete': [('readonly', True)],
        'prepare': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    
    exam_session_id = fields.Many2one(
        comodel_name='oe.exam.session',
        string="Exam Session", 
        required=True, ondelete='cascade', index=True, copy=False,
        domain="[('state','=','progress')]"
    )

    course_id = fields.Many2one(related='exam_session_id.course_id')

    use_batch = fields.Boolean(related='course_id.use_batch_subject')
    batch_id = fields.Many2one('oe.school.course.batch', string='Batch', 
                               domain="[('course_id','=',course_id)]"
                              )

    use_section = fields.Boolean(related='course_id.use_section')
    section_id = fields.Many2one('oe.school.course.section', string='Section', 
                                 domain="[('course_id','=',course_id)]"
                              )

    subject_ids = fields.Many2many('oe.school.subject', string='Subjects', compute='_compute_subject_ids', store=True)
    subject_id = fields.Many2one('oe.school.subject', string='Subject',
                                 domain="[('id','in',subject_ids)]",
                                 required=True,
                                )
    
    marks_min = fields.Float(string='Minimum Marks', required=True, )
    marks_max = fields.Float(string='Maximum Marks', required=True, )
    date_start = fields.Datetime(string='Start Time', required=True, )
    date_end = fields.Datetime(string='End Time', required=True, )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('schedule', 'Scheduled'),
        ('complete', 'Completed'),
        ('prepare', 'Result Prepared'),
        ('done', 'Result Updated'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        
        default=lambda self: self.env.company)
    # Address Fields
    exam_mode = fields.Selection([
        ('physical', 'Physical'),
        ('online', 'Online'),
    ], string='Mode', default='physical', required=True)
    address_id = fields.Many2one('res.partner', 'Work Address', 
                                 compute="_compute_address_id", 
                                 store=True, readonly=False, 
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    exam_location_id = fields.Many2one('oe.school.building.room', 'Exam Location', 
                                       compute="_compute_exam_location_id", 
                                      
                                       store=True, readonly=False,
                                       domain="[('building_id.address_id', '=', address_id)]")

    exam_hours = fields.Float(string='Exam Hours', 
                              compute='_compute_exam_hours', 
                              store=True, readonly=True)

    attendees_count = fields.Integer('Attendees',)
    exam_attendee_ids = fields.One2many('oe.exam.attendees', 'exam_id', string='Attendees', )
    
    exam_result_line = fields.One2many('oe.exam.result', 'exam_id', string='Exams', )
    exam_result_count = fields.Integer('Exam Result Count', compute='_compute_exam_result')
    
    # ----------------------------------------
    # Compute Methods
    # ----------------------------------------
    
    @api.depends('company_id')
    def _compute_address_id(self):
        for exam in self:
            address = exam.company_id.partner_id.address_get(['default'])
            exam.address_id = address['default'] if address else False

    @api.depends('address_id')
    def _compute_exam_location_id(self):
        to_reset = self.filtered(lambda e: e.address_id != e.exam_location_id.building_id.address_id)
        to_reset.exam_location_id = False

    @api.depends('date_start', 'date_end')
    def _compute_exam_hours(self):
        for exam in self:
            if exam.date_start and exam.date_end:
                delta = exam.date_end - exam.date_start
                exam.exam_hours = delta.total_seconds() / 3600.0
            else:
                exam.exam_hours = False

    def _compute_exam_result(self):
        for record in self:
            record.exam_result_count = len(record.exam_result_line)

    @api.depends('course_id')
    def _compute_subject_ids(self):
        for attendance in self:
            if attendance.course_id:
                subject_lines = attendance.env['oe.school.course.subject.line'].search([
                    ('course_id', '=', attendance.course_id.id)
                ])
                attendance.subject_ids = subject_lines.mapped('subject_id')
            else:
                attendance.subject_ids = False
                
    # CRUD Operations
    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError("You cannot delete a record with applicants when the status is not 'Draft'.")
        return super(Exam, self).unlink()

    @api.constrains('exam_hours')
    def _check_exam_hours(self):
        for record in self:
            if record.exam_hours < 0:
                raise ValidationError("The End date cannot be less than start date.")

    
    # Action Buttons
    def button_draft(self):
        self.write({'state': 'draft'})

    def button_schedule(self):
        self.write({'state': 'schedule'})

    def button_close(self):
        self.write({'state': 'complete'})
        
    def button_cancel(self):
        self.write({'state': 'draft'})

    def button_prepare_result(self):
        student_ids = self.env['res.partner'].search([('course_id','=',self.exam_session_id.course_id.id),('batch_id','=',self.batch_id.id)])
        #raise UserError(student_ids)
        for student in student_ids:
            exam_result = self.env['oe.exam.result'].create({
                'student_id': student.id,
                'exam_id': self.id,
                'attendance_status': 'present',
                'marks': 0,
            })
        self.write({'state': 'prepare'})

    def button_complete_result(self):
        for exam in self:
            if any(er.marks == 0 for er in exam.exam_result_line.filtered(lambda e: e.attendance_status == 'present')):
                raise UserError("One or more student's marks are not updated.")
        self.write({'state': 'done'})

    def action_view_exam_results(self):
        context = {
            'default_exam_id': self.id,
            'exam_id': self.id,
        }
        action = {
            'name': 'Exam Result',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'oe.exam.result',
            'type': 'ir.actions.act_window',
            'context': context,
        }
        return action

    @api.model
    def _fields_view_get_results(self, arch):
        arch = super(Exam, self)._fields_view_get_results(arch)

        doc = etree.fromstring(arch)

        if doc.xpath("//field[@name='credit_points']"):
            return arch

        replacement_xml = """
            <field name='credit_points' placeholder="%(placeholder)s" class="o_credit_points"  />
        """

        replacement_data = {
            'placeholder': _('Credit Points'),
        }

        for results_node in doc.xpath("//group[@name='results_group']"):
            replacement_formatted = replacement_xml % replacement_data
            for replace_node in etree.fromstring(replacement_formatted).getchildren():
                results_node.append(replace_node)

        arch = etree.tostring(doc, encoding='unicode')
        return arch
        
    def button_open_result(self):
        
        #view_id = self.env['ir.ui.view'].search([('name','=','dynamic_extend_result_tree_view')])
        #if view_id:
        #    view_id.unlink()
            
        #if self.batch_id.enable_credit_points:
        #    self.open_dynamic_tree_view()

        #view_id = self.env.ref('de_school_exam.exam_result_tree_view')
        #view_id.render()
        #view_id.load()
        #self.env.ref('de_school_exam.exam_result_tree_view').arch

        if self.batch_id.enable_credit_points:
            #action['action_id'] = self.env.ref('de_school_exam.action_exam_result_grade').id
            #raise UserError('grade')
            action = self.env['ir.actions.actions']._for_xml_id('de_school_exam.action_exam_result_grade')
        else:
            #action['action_id'] = self.env.ref('de_school_exam.action_exam_result').id
            action = self.env['ir.actions.actions']._for_xml_id('de_school_exam.action_exam_result')
        
        context = {
            'default_exam_id': self.id,
            'exam_id': self.id,
            'create': False,
            'delete': False,
        }
        action['context'] = context
        #action = {
        #    'name': 'Exam Result',
        #    'view_type': 'form',
        #    'view_mode': 'tree,form',
        #    'res_model': 'oe.exam.result',
        #    'type': 'ir.actions.act_window',
        #    'context': context,
        #}
        return action
        

    def open_dynamic_tree_view(self):
        tree_view_id = self.env['ir.ui.view'].create({
            'name': 'dynamic_extend_result_tree_view',
            'model': 'oe.exam.result',
            'type': 'tree',
            'inherit_id': self.env.ref('de_school_exam.exam_result_tree_view').id,
            'arch': """
                <data>
                    <field name="marks" position="after">
                        <field name="credit_points" />
                    </field>
                </data>
            """
        })

    def action_view_attendees(self):
        action = self.env.ref('de_school_exam.action_exam_attendees').read()[0]
        action.update({
            'name': 'Exam Attendees',
            'view_mode': 'tree',
            'res_model': 'oe.exam.attendees',
            'type': 'ir.actions.act_window',
            'domain': [('exam_id','=',self.id)],
            'context': {
                'create': False,
                'delete': False,
            },
            
        })
        return action
