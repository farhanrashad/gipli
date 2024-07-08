# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar

from collections import defaultdict, OrderedDict
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare


class Location(models.Model):
    _inherit = "stock.location"

    is_hostel = fields.Boolean(default=False)

    unit_usage = fields.Selection([
        ('view', 'View'),
        ('internal', 'Location'),
    ], string='Location Type', 
                            )
    
    unit_facility_ids = fields.Many2many(
        'oe.hostel.unit.facility',
        string='Facilities',
        domain="[('use_unit','!=',True)]"
    )

    # Building Attributes
    location = fields.Char(string='Location')

    @api.onchange('unit_usage')
    def _onchange_unit_usage(self):
        if self.unit_usage:
            self.usage = self.unit_usage