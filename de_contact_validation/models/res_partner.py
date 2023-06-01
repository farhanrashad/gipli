# -*- coding: utf-8 -*-

from odoo import models, fields, api
import base64
import collections
import datetime
import hashlib
import pytz
import threading
import re
import requests
from lxml import etree
from random import randint
from werkzeug import urls
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.modules import get_module_resource
from odoo.osv.expression import get_unaccent_wrapper
from odoo.exceptions import UserError, ValidationError

class Partner(models.Model):
    _inherit = 'res.partner'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
    ], string='Status', copy=False, index=True, default='draft')

    def action_to_approve(self):
        self.write({
            'state' : 'to_approve',
            # 'active' : False,
        })

    def action_approved(self):
        self.write({
            'state': 'approved',
        })
    def action_draft(self):
        self.write({
            'state': 'draft',
        })

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = [('name', operator, name),('state', '=', 'approved')] + args
            
        return super(Partner, self)._search(args, limit=limit, access_rights_uid=name_get_uid)
    