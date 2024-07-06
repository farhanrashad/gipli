# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

class HostelUnit(models.Model):
    _name = 'oe.hostel.unit.facility.type'
    _description = 'Unit Facility Type'

    name = fields.Char(required=True)
    
class HostelUnit(models.Model):
    _name = 'oe.hostel.unit.facility'
    _description = 'Unit Facility'

    name = fields.Char(required=True)
    facility_type_id = fields.Many2one('oe.hostel.unit.facility.type', string='Facility Type', required=True)
    use_unit = fields.Boolean('Used for Unit')
    active = fields.Boolean(default=True)