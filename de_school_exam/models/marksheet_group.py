# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MarksheetGroup(models.Model):
    _name = 'oe.exam.msheet.group'
    _description = 'Marksheet Group'
    _order = "name asc"

    name = fields.Char(string='Name', required=True)
    ms_group_line = fields.One2many('oe.exam.msheet.group.line', 'ms_group_id', string='Marksheet Group Lines')

class MarksheetGroupLine(models.Model):
    _name = 'oe.exam.msheet.group.line'
    _description = 'Marksheet Group Line'

    ms_group_id = fields.Many2one('oe.exam.msheet.group', string='Marksheet Group')
    exam_type_id = fields.Many2one('oe.exam.type', string='Exam Type', required=True)
    grade_weightage = fields.Float(string='Weightage', required=True)
    