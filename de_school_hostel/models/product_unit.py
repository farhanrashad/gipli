# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import itertools
import logging
from collections import defaultdict

from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_hostel_unit = fields.Boolean(default=False)

    tracking_serial = fields.Boolean(string='Tracking Serial', compute='_compute_tracking_serial', inverse='_inverse_tracking_serial')

   
    @api.depends('tracking')
    def _compute_tracking_serial(self):
        for record in self:
            record.tracking_serial = record.tracking == 'serial'

    def _inverse_tracking_serial(self):
        for record in self:
            if record.tracking_serial:
                record.tracking = 'serial'
            else:
                record.tracking = 'none'
            