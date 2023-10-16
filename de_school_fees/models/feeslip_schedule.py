# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class FeeslipSchedule(models.Model):
    _name = "oe.feeslip.schedule"
    _description = 'Fee Schedule'

    batch_id = fields.Many2one('oe.school.course.batch', string='Batch', required=True)
    course_id = fields.Many2one('oe.school.course', string='Course', related='batch_id.course_id')
    fee_struct_id = fields.Many2one('oe.fee.struct', string='Fee Structure', required=True)
    date = fields.Date(string='Date Due', default=lambda self: fields.Date.today(), required=True)