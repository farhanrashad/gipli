# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Course(models.Model):
    _inherit = 'oe.school.course'

    exam_grade_id = fields.Many2one('oe.exam.grade', string='Grade')