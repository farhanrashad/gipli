# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class WorkoutActivity(models.Model):
    _name = 'gym.workout.activity'
    _description = 'Workout Activity'

    name = fields.Char(string='Name', required=True)
    wo_activity_type_id = fields.Many2one('gym.activity.type', string='Activity Type', copy=False, required=True)

    