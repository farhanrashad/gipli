# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, date_utils, email_split, email_re
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from collections import defaultdict
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import ast
import json
import re
import warnings
    
    
class AccountMove(models.Model):
    _inherit= 'account.move'
    
    
class AccountMoveLine(models.Model):
    _inherit= 'account.move.line'
    
    allocation_move_line_id = fields.Many2one('account.move.line', string='Allocation Move Line')
    payment_matching = fields.Boolean(string='Payment Matching')
    
    