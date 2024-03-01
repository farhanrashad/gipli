# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class GYMActivityType(models.Model):
    _name = 'gym.activity.type'
    _description = 'Activity Type'

    name = fields.Char(string='Name', required=True)

    