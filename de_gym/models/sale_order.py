# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, date
from odoo import api, fields, models, _
# -*- coding: utf-8 -*-

from odoo.tools import float_compare, format_datetime, format_time
from pytz import timezone, UTC
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class GYMOrder(models.Model):
    _inherit = 'sale.order'

    gym_order = fields.Boolean("GYM Subscription")