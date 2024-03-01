# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class NuitritionMealType(models.Model):
    _name = 'gym.nutr.meal.type'
    _description = 'Nutrition Meal Type'
    _order = "id"

    name = fields.Char(string='Name', required=True)