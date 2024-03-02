# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class GYMClassType(models.Model):
    _name = 'gym.class.type'
    _description = 'GYM Class Type'
    _order = "id"

    name = fields.Char(string='Name', required=True)