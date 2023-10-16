# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class FeeslipSchedule(models.Model):
    _name = "oe.feeslip.schedule"
    _description = 'Fee Schedule'

    course_id = fields.Many2one('oe.school.course', string='Course', required=True)
    batch_id = fields.Many2one('oe.school.course.batch', string='Batch', required=True)
    date = fields.Date(string='Date', default=lambda self: fields.Date.today(), required=True)