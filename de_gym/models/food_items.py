# -*- coding: utf-8 -*-

from datetime import timedelta, date
from odoo import api, fields, models, _

from odoo.tools import float_compare, format_datetime, format_time
from pytz import timezone, UTC
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class GymFoodItem(models.Model):
    _name = "gym.food.item"
    _description = "Food Item"
    _order = "name, id desc"

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string="Description")
    food_item_line = fields.One2many('gym.food.item.line', 'food_item_id', string='Food Item Line')
    active = fields.Boolean(default=True)

class GymFoodItemLine(models.Model):
    _name = "gym.food.item.line"
    _description = "Food Item Line"

    food_item_id = fields.Many2one('gym.food.item', string='Food Item', 
                                   required=True, ondelete='cascade')
    nutrient_id = fields.Many2one('gym.nutrients', string='Nutrient', required=True, copy=False,  ondelete='restrict',)
    quantity = fields.Float(string="Qty", digits=(5, 2), required=True, default="1.0")
    uom_id = fields.Many2one("uom.uom", string="UOM", required=True,
                            domain="[('category_id.name','=','Weight')]"
                            )