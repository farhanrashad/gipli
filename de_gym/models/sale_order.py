# -*- coding: utf-8 -*-

from datetime import timedelta, date
from odoo import api, fields, models, _

from odoo.tools import float_compare, format_datetime, format_time
from pytz import timezone, UTC
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class GYMOrder(models.Model):
    _inherit = 'sale.order'

    gym_order = fields.Boolean("GYM Subscription")