# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'
    _order = 'date asc'
