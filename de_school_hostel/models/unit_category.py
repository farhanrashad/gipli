# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

class HostelUnitType(models.Model):
    _name = 'oe.hostel.unit.category'
    _description = 'Unit category'

    name = fields.Char(required=True)
    usage = fields.Selection([
        ('building', 'Building'),
        ('floor', 'Floor'),
        ('room', 'Room'),
    ], string='Usage',
        default='room', index=True, required=True,
    )