# -*- coding: utf-8 -*-

from babel.dates import format_date
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
        
class Exam(models.Model):
    _name = 'oe.exam'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Exam'
    _rec_name = 'subject_id'

    READONLY_STATES = {
        'progress': [('readonly', True)],
        'close': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    
    exam_session_id = fields.Many2one(
        comodel_name='oe.exam.session',
        string="Exam Session", states=READONLY_STATES,
        required=True, ondelete='cascade', index=True, copy=False)

    batch_id = fields.Many2one(
        comodel_name='oe.school.course.batch',
        string="Batch", required=True,
        states=READONLY_STATES,
        change_default=True, ondelete='restrict', )
    
    subject_id = fields.Many2one(
        comodel_name='oe.school.course.subject',
        string="Subject", required=True, states=READONLY_STATES,
        change_default=True, ondelete='restrict', )
    marks_min = fields.Float(string='Minimum Marks', required=True, states=READONLY_STATES,)
    marks_max = fields.Float(string='Maximum Marks', required=True, states=READONLY_STATES,)
    date_start = fields.Datetime(string='Start Time', required=True, states=READONLY_STATES,)
    date_end = fields.Datetime(string='End Time', required=True, states=READONLY_STATES,)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'Open'),
        ('close', 'Closed'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        states=READONLY_STATES,
        default=lambda self: self.env.company)
    # Address Fields
    address_id = fields.Many2one('res.partner', 'Work Address', 
                                 compute="_compute_address_id", 
                                 store=True, readonly=False, states=READONLY_STATES,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    exam_location_id = fields.Many2one('oe.school.building.room', 'Exam Location', 
                                       compute="_compute_exam_location_id", 
                                       states=READONLY_STATES,
                                       store=True, readonly=False,
                                       domain="[('building_id.address_id', '=', address_id)]")

    exam_hours = fields.Float(string='Exam Hours', 
                              compute='_compute_exam_hours', 
                              store=True, readonly=True)
    
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


    # ----------------------------------------
    # Compute Methods
    # ----------------------------------------
    @api.depends('date_start', 'date_end')
    def _compute_exam_hours(self):
        for exam in self:
            if exam.date_start and exam.date_end:
                delta = exam.date_end - exam.date_start
                exam.exam_hours = delta.total_seconds() / 3600.0
            else:
                exam.exam_hours = False
                
            
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