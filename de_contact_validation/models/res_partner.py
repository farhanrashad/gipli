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


from string import digits
from werkzeug.urls import url_encode

from odoo import api, fields, models, _
from lxml import etree

from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.modules.module import get_module_resource
import json
import simplejson

class Partner(models.Model):
    _inherit = 'res.partner'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
    ], string='Status', copy=False, index=True, default='draft')

    no_edit_mode = fields.Boolean(string='Allow Edit')

    # ------------------------------------------
    # ------------ Action Buttons --------------
    # ------------------------------------------
    def button_submit(self):
        self.write({
            'state' : 'to_approve',
            'no_edit_mode': True,
        })

    def button_confirm(self):
        self.write({
            'state': 'approved',
        })
        
    def button_draft(self):
        self.write({
            'state': 'draft',
            'no_edit_mode': False,
        })
    
    def button_refuse(self):
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

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super(Partner, self).get_view(view_id=view_id, view_type=view_type, **options)
        doc = etree.XML(res['arch'])
        if view_type == 'form':
            for node in doc.xpath("//field"):
                #modifiers = simplejson.loads(node.get("modifiers"))
                modifiers = json.loads(node.attrib.pop('modifiers', '{}'))
                if 'readonly' not in modifiers:
                    modifiers['readonly'] = [['no_edit_mode','!=',False]]
                else:
                    if type(modifiers['readonly']) != bool:
                        modifiers['readonly'].insert(0, '|')
                        modifiers['readonly'] += [['no_edit_mode','!=',False]]
                #node.set('modifiers', simplejson.dumps(modifiers))
                if modifiers:
                    node.set('modifiers', json.dumps(modifiers))
                res['arch'] = etree.tostring(doc)
        return res
    