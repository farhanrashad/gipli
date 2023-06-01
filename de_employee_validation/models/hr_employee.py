# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
from random import choice
from string import digits
from werkzeug.urls import url_encode

from odoo import api, fields, models, _
from lxml import etree

from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.modules.module import get_module_resource
import json
import simplejson

class HrEmployee(models.Model):
    _inherit = "hr.employee"
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('expired','Expired'),
    ], string='Status', index=True, readonly=True, tracking=True, copy=False, default='draft', required=True, help='Employee State')
    no_edit_mode = fields.Boolean(string='Allow Edit', default=False)
        
    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super(HrEmployee, self).get_view(view_id=view_id, view_type=view_type, **options)
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
    
    def name_get(self):
        #if self.check_access_rights('read', raise_exception=False):
        #    return super(HrEmployee, self).name_get()
        return self.env['hr.employee.public'].browse(self.filtered(lambda x: x.state == 'approved').ids).name_get()
    
    # ------------------------------------------
    # ------------ Action Buttons --------------
    # ------------------------------------------
    def button_submit(self):
        self.write({
            'state' : 'pending',
            'no_edit_mode': True,
        })

    def button_confirm(self):
        self.write({
            'state': 'approved',
        })
        
    def button_expire(self):
        self.write({
            'state': 'expired',
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