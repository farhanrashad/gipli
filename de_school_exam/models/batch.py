# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CourseBatch(models.Model):
    _inherit = 'oe.school.course.batch'

    exam_grade_id = fields.Many2one('oe.exam.grade', string='Grade')
    exam_batch_grade_line = fields.One2many('oe.exam.batch.grade', 'couse_batch_id', string='Batch Grade Lines')

class BatchGradeLine(models.Model):
    _name = 'oe.exam.batch.grade'
    _description = 'Exam Grading Line'

    couse_batch_id = fields.Many2one('oe.school.couse.batch', string='Batch')
    name = fields.Char(string='Grade', required=True)
    score_min = fields.Float(string='Min Score (%)')
    credit_points = fields.Float(string='Credit Points')