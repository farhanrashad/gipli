# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AssignmentSubmit(models.Model):
    _name = 'oe.assignment.submit'
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
    
    batch_id = fields.Many2one(
        comodel_name='oe.school.course.batch',
        string="Batch",
        change_default=True, ondelete='restrict')

    attachment = fields.Binary(string='Attachment', attachment=True)    
    description = fields.Html(string='description')
    