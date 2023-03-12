# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero
from odoo.tools.misc import formatLang, format_date, get_lang

#from datetime import datetime, timedelta
#import datetime

class HREOSType(models.Model):
    _name = "hr.eos.type"
    _description = "Employee End of Service Type"
    _order = 'name asc'
    
    name = fields.Char(required=True)
    
class HREOSType(models.Model):
    _name = "hr.eos.term.type"
    _description = "Employee Terminiation Type"
    _order = 'name asc'
    
    name = fields.Char(required=True)
    
class HREOSChecklist(models.Model):
    _name = "hr.eos.checklist"
    _description = "End of Service Checklist"
    _order = 'name asc'
    
    name = fields.Char(required=True)
    
    