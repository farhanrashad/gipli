# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AssignmentSubmit(models.Model):
    _name = 'oe.assignment.line'
    _description = 'Assignment Submission'

    
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
    student_id = fields.Many2one(
        comodel_name='res.partner',
        domain="[('is_student','=',True)]",
        string="Batch",
        change_default=True, ondelete='restrict')
    
    batch_id = fields.Many2one(
        comodel_name='oe.school.course.batch',
        string="Batch",
        change_default=True, ondelete='restrict')

    attachment = fields.Binary(string='Attachment', attachment=True)    
    description = fields.Html(string='description')
    assignment_status = fields.Selection([
        ('draft', 'Pending'),
        ('submit', 'Submitted'),
        ('cancel', 'Cancelled')
    ], string='Assignment Status', )
    