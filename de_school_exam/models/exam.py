# -*- coding: utf-8 -*-

from babel.dates import format_date
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
        
class Exam(models.Model):
    _name = 'oe.exam'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Exam'

    READONLY_STATES = {
        'progress': [('readonly', True)],
        'close': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    
    exam_session_id = fields.Many2one(
        comodel_name='oe.exam.session',
        string="Exam Session",
        required=True, ondelete='cascade', index=True, copy=False)
    subject_id = fields.Many2one(
        comodel_name='oe.school.course.subject',
        string="Subject",
        change_default=True, ondelete='restrict', )
    marks_min = fields.Float(string='Minimum Marks', required=True)
    marks_max = fields.Float(string='Maximum Marks', required=True)
    date_start = fields.Datetime(string='Start Time')
    date_end = fields.Datetime(string='End Time')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'Open'),
        ('close', 'Closed'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)
    # Address Fields
    address_id = fields.Many2one('res.partner', 'Work Address', compute="_compute_address_id", store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    exam_location_id = fields.Many2one('oe.school.building.room', 'Exam Location', compute="_compute_exam_location_id", store=True, readonly=False,
    domain="[('building_id.address_id', '=', address_id)]")
    
    # Compute Methods
    @api.depends('company_id')
    def _compute_address_id(self):
        for exam in self:
            address = exam.company_id.partner_id.address_get(['default'])
            exam.address_id = address['default'] if address else False

    @api.depends('address_id')
    def _compute_exam_location_id(self):
        to_reset = self.filtered(lambda e: e.address_id != e.exam_location_id.building_id.address_id)
        to_reset.exam_location_id = False

    def _compute_exam(self):
        for record in self:
            record.exam_count = len(record.exam_line)
            
    # CRUD Operations
    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise exceptions.UserError("You cannot delete a record with applicants when the status is not 'Draft'.")
        return super(ExamSession, self).unlink()

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

    

