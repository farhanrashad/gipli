# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class GYMNutrients(models.Model):
    _name = 'gym.nutrients'
    _description = 'Nutrients'

    name = fields.Char(string='Name', required=True)

    