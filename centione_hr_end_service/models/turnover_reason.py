# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)

class TurnoverReason(models.Model):
    _name = 'turnover.reason'

    name = fields.Char(string="Name", required=False, )
