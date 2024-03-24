# -*- coding: utf-8 -*-

import requests
from odoo import api, fields, models, Command
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class ResPartner(models.Model):
    _inherit = 'res.partner'

    calendly_uri = fields.Char(string='Calendly URI')