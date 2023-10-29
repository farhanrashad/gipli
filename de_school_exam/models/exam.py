# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Exam(models.Model):
    _name = 'oe.exam'
    _description = 'Exam'
    _order = "name asc"

    READONLY_STATES = {
        'progress': [('readonly', True)],
        'close': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    
    name = fields.Char(string='Name', required=True)
    marks_min = fields.Float(string='Minimum Marks', required=True)
    marks_max = fields.Float(string='Maximum Marks', required=True)
    course_id = fields.Many2one(
        comodel_name='oe.school.course',
        string="Course",
        change_default=True, ondelete='restrict', )
    exam_type_id = fields.Many2one('oe.exam.type', string='Exam Type', required=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'Open'),
        ('close', 'Closed'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
    # Address Fields
    address_id = fields.Many2one('res.partner', 'Work Address', compute="_compute_address_id", store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    exam_location_id = fields.Many2one('oe.school.building.room', 'Exam Location', compute="_compute_exam_location_id", store=True, readonly=False,
    domain="[('building_id.address_id', '=', address_id)]")



    exam_line = fields.One2many('oe.exam.line', 'exam_id', string='Exam Line')

    # Compute Methods
    @api.depends('company_id')
    def _compute_address_id(self):
        for exam in self:
            address = exam.company_id.partner_id.address_get(['default'])
            exam.address_id = address['default'] if address else False

    @api.depends('address_id')
    def _compute_work_location_id(self):
        to_reset = self.filtered(lambda e: e.address_id != e.exam_location_id.building_id.address_id)
        to_reset.exam_location_id = False

    # CRUD Operations
    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise exceptions.UserError("You cannot delete a record with applicants when the status is not 'Draft'.")
        return super(Exam, self).unlink()

    # Action Buttons
    def button_draft(self):
        self.write({'state': 'draft'})
        return {}

    def button_open(self):
        self.write({'state': 'progress'})
        return {}

    def button_close(self):
        self.write({'state': 'close'})
        return {}
        
    def button_cancel(self):
        self.write({'state': 'draft'})
        return {}
        
class ExamLine(models.Model):
    _name = 'oe.exam.line'
    _description = 'Exam Line'

    exam_id = fields.Many2one(
        comodel_name='oe.exam',
        string="Exam Reference",
        required=True, ondelete='cascade', index=True, copy=False)
    subject_id = fields.Many2one(
        comodel_name='oe.school.course.subject',
        string="Subject",
        change_default=True, ondelete='restrict', )
    marks_min = fields.Float(string='Minimum Marks', required=True)
    marks_max = fields.Float(string='Maximum Marks', required=True)
    date_start = fields.Datetime(string='Start Time')
    date_end = fields.Datetime(string='End Time')

    

