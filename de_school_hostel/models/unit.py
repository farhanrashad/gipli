# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


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

    #unit_line = fields.One2many(
    #    comodel_name='oe.hostel.unit.line',
    #    inverse_name='unit_id',
    #    string="Unit Lines",
    #    copy=True, auto_join=True)

    unit_facility_ids = fields.Many2many(
        'oe.hostel.unit.facility',
        string='Facilities'
    )

    
    room_capacity = fields.Integer(string='Number of Rooms')
    
    # Building Attributes
    location = fields.Char(string='Location')
    floor_capacity = fields.Integer(string='Number of Floors')
    building_type = fields.Selection([
        ('hostel', 'Hostel'),
        ('dormitory', 'Dormitory'),
        ('residential', 'Residential'),
    ], string='Building Type')
    

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
