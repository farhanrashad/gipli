# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import random

from babel.dates import format_date
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.release import version


class ElectionYear(models.Model):
    _name = "vote.elect.year"
    _description = "Election Year"
    _order = "name asc"

    active = fields.Boolean(default=True)
    name = fields.Char(string='Name', required=True, index='trigram', translate=True)
    date_elect = fields.Date(string='Election Date',  store=True, readonly=False, required=True)
    description = fields.Html(string='Description')