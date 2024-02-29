# -*- coding: utf-8 -*-

from datetime import timedelta, date
from odoo import api, fields, models, _

from odoo.tools import float_compare, format_datetime, format_time
from pytz import timezone, UTC
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class GYMNutrients(models.Model):
    _name = 'gym.nutrients'
    _description = 'Nutrients'

    name = fields.Char(string='Name', required=True)