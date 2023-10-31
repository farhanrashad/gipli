# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Assignment(models.Model):
    _name = 'oe.assignment'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Assignment'

    READONLY_STATES = {
            'publish': [('readonly', True)],
            'close': [('readonly', True)],
            'cancel': [('readonly', True)],
        }
    
    name = fields.Char(string='Name', required=True, states=READONLY_STATES,)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('publish', 'Published'),
        ('close', 'Close'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
    course_id = fields.Many2one(
        comodel_name='oe.school.course',
        string="Course",
        change_default=True, ondelete='restrict', states=READONLY_STATES,)
    subject_id = fields.Many2one(
        comodel_name='oe.school.course.subject',
        string="Subject", required=True, states=READONLY_STATES,
        domain="[('course_ids','in',course_id)]",
        change_default=True, ondelete='restrict', )

    batch_ids = fields.Many2many(
        comodel_name='oe.school.course.batch',
        relation='assignment_batch_ids',
        column1='assignment_id',
        column2='batch_id',
        string='Batches',
        help='Batches to assign assignments'
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        states=READONLY_STATES,
        default=lambda self: self.env.company)
    
    note = fields.Text('Description')
    date_due = fields.Datetime(string='Due Date', required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now, required=True, help='Assignment Date')
    date_publish = fields.Datetime(string='Publish Date')

    assignment_line_ids = fields.One2many('oe.assignment.line', 'assignment_id', string='Assignments', states=READONLY_STATES,)
    assignment_count = fields.Integer('Assignment Count', compute='_compute_exam')
    
    assignment_submit_line_ids = fields.One2many(  # /!\ assignment_submit_line_ids is just a subset of assignment_line_ids.
        'oe.assignment.line',
        'assignment_id',
        string='Submit lines',
        copy=False,
        states=READONLY_STATES,
        domain=[('assignment_status', 'in', ('submit'))],
    )
    assignment_submit_count = fields.Integer('Assignment Count', compute='_compute_exam')

    # Action Buttons
    def button_draft(self):
        self.write({'state': 'draft'})

    def button_publish(self):
        self.write({'state': 'publish'})

    def button_close(self):
        self.write({'state': 'close'})
        
    def button_cancel(self):
        self.write({'state': 'draft'})

    def action_view_assigned_assignments(self):
        pass
        