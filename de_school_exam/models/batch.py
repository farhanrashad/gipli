# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CourseBatch(models.Model):
    _inherit = 'oe.school.course.batch'

    exam_grade_id = fields.Many2one('oe.exam.grade', string='Grade')
    enable_score = fields.Boolean(related='exam_grade_id.enable_score')
    enable_credit_points = fields.Boolean(related='exam_grade_id.enable_credit_points')

    exam_grade_line = fields.One2many(related='exam_grade_id.exam_grade_line')