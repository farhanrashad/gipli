# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class WorkoutLevel(models.Model):
    _name = 'gym.workout.level'
    _description = 'Workout Level'

    name = fields.Char(string='Name', required=True)

    