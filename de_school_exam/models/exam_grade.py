# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ExamGrade(models.Model):
    _name = 'oe.exam.grade'
    _description = 'Exam Grading System'

    name = fields.Char(string='Name', required=True)