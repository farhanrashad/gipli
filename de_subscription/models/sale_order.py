# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, date
from odoo import api, fields, models, _
from odoo.tools import float_compare, format_datetime, format_time
from pytz import timezone, UTC


class SubscriptionOrder(models.Model):
    _inherit = 'sale.order'

    is_subscription = fields.Boolean("Subscription")