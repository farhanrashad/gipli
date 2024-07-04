# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

# Subset of partner fields: sync all or none to avoid mixed addresses
PARTNER_ADDRESS_FIELDS_TO_SYNC = [
    'street',
    'street2',
    'city',
    'zip',
    'state_id',
    'country_id',
]

class HostelUnit(models.Model):
    _name = 'oe.hostel.unit'
    _description = 'Hostel Units'
    _parent_name = "unit_id"
    _parent_store = True
    _order = 'complete_name, id'
    _rec_name = 'complete_name'
    _rec_names_search = ['complete_name']
    _check_company_auto = True

    
    name = fields.Char(string='Unit Name', required=True, index=True, translate=True)
    complete_name = fields.Char("Full Name", compute='_compute_complete_name', recursive=True, store=True)
    unit_id = fields.Many2one('oe.hostel.unit', 'Parent Unit', index=True, 
                              ondelete='cascade', check_company=True,
                              help="The parent unit that includes this unit.")
    child_ids = fields.One2many('oe.hostel.unit', 'unit_id', 'Contains')
    parent_path = fields.Char(index=True, unaccent=False)
    unit_type = fields.Selection([
        ('building', 'Building'),
        ('floor', 'Floor'),
        ('room', 'Room'),
    ], string='Type',
        default='room', index=True, required=True,
    )

    active = fields.Boolean('Active', default=True, help="By unchecking the active field, you may hide a unit without deleting it.")
    company_id = fields.Many2one('res.company', 'Company',
        default=lambda self: self.env.company, index=True,
        help='Let this field empty if this unit is shared between companies')



    code = fields.Char(string=' Code', size=5, required=True)  # Define size as needed
    capacity = fields.Integer(string='Capacity', required=True, default=10)
    description = fields.Text(string='Description', help="Detailed description of the building")

    room_capacity = fields.Integer(string='Number of Rooms')
    
    # Building Attributes
    #location = fields.Char(string='Location')
    floor_capacity = fields.Integer(string='Number of Floors')
    building_type = fields.Selection([
        ('hostel', 'Hostel'),
        ('dormitory', 'Dormitory'),
        ('residential', 'Residential'),
    ], string='Building Type')
    # Address fields
    partner_id = fields.Many2one(
        'res.partner', string='Customer', check_company=True, index=True, tracking=10,)
    street = fields.Char('Street', compute='_compute_partner_address_values', readonly=False, store=True)
    street2 = fields.Char('Street2', compute='_compute_partner_address_values', readonly=False, store=True)
    zip = fields.Char('Zip', change_default=True, compute='_compute_partner_address_values', readonly=False, store=True)
    city = fields.Char('City', compute='_compute_partner_address_values', readonly=False, store=True)
    state_id = fields.Many2one(
        "res.country.state", string='State',
        compute='_compute_partner_address_values', readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country',
        compute='_compute_partner_address_values', readonly=False, store=True)
    

    # Floor Attributes
    floor_number = fields.Integer(string='Floor Number')
    cleanliness_status = fields.Selection([
        ('clean', 'Clean'),
        ('average', 'Average'),
        ('dirty', 'Dirty'),
    ], string='Cleanliness Status')
    occupancy_status = fields.Selection([
        ('occupied', 'Occupied'),
        ('vacant', 'Vacant'),
        ('under_maintenance', 'Under Maintenance'),
    ], string='Occupancy Status')
    

    # Room Fields
    room_type = fields.Selection([
        ('single', 'Single'),
        ('double', 'Double'),
        ('triple', 'Triple'),
        ('suite', 'Suite'),
        ('dormitory', 'Dormitory'),
    ], string='Room Type', required=True)


    @api.depends('name', 'unit_id.complete_name', 'unit_type')
    def _compute_complete_name(self):
        for unit in self:
            if unit.unit_id and unit.unit_type != 'building':
                unit.complete_name = '%s/%s' % (unit.unit_id.complete_name, unit.name)
            else:
                unit.complete_name = unit.name

    # Address Related Methods
    @api.depends('partner_id')
    def _compute_partner_address_values(self):
        for unit in self:
            unit.update(unit._prepare_address_values_from_partner(unit.partner_id))

    def _prepare_address_values_from_partner(self, partner):
        if any(partner[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC):
            values = {f: partner[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC}
        else:
            values = {f: self[f] for f in PARTNER_ADDRESS_FIELDS_TO_SYNC}
        return values