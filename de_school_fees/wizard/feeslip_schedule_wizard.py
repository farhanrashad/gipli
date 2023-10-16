# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class FeeslipScheduleWizard(models.TransientModel):
    _name = "oe.feeslip.schedule.wizard"
    _description = 'Fee Schedule Wizard'

    course_id = fields.Many2one('oe.school.course', string='Course', required=True)

    def action_schedule(self):
        pass