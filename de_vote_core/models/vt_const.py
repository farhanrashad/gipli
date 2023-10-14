# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar

from collections import defaultdict, OrderedDict
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare


class constituency(models.Model):
    _name = "vt.const"
    _description = "constituencies"
    _parent_name = "const_id"
    _parent_store = True
    _order = 'complete_name, id'
    _rec_name = 'complete_name'
    _rec_names_search = ['complete_name', 'barcode']
    _check_company_auto = True

    @api.model
    def default_get(self, fields):
        res = super(Location, self).default_get(fields)
        if 'barcode' in fields and 'barcode' not in res and res.get('complete_name'):
            res['barcode'] = res['complete_name']
        return res

    name = fields.Char('Constituency Name', required=True)
    complete_name = fields.Char("Full Constituency Name", compute='_compute_complete_name', recursive=True, store=True)
    active = fields.Boolean('Active', default=True, help="By unchecking the active field, you may hide a constituency without deleting it.")
    const_id = fields.Many2one(
        'vt.const', 'Parent Constituency', index=True, ondelete='cascade', check_company=True,
        help="The parent Constituency that includes this Constituency.")
    comment = fields.Html('Additional Information')
    barcode = fields.Char('Barcode', copy=False)

    _sql_constraints = [('barcode_company_uniq', 'unique (barcode,company_id)', 'The barcode for a location must be unique per company !')]
    

