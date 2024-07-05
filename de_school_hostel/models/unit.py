# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

class HostelUnitType(models.Model):
    _name = 'oe.hostel.unit.type'
    _description = 'Unit Type'

    name = fields.Char(required=True)
    usage = fields.Selection([
        ('building', 'Building'),
        ('floor', 'Floor'),
        ('room', 'Room'),
    ], string='Usage',
        default='room', index=True, required=True,
    )

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

    status = fields.Selection([
        ('available', 'Available'), 
        ('reserve', 'Reserved'), 
        ('use', 'In Use'),
        ('out_of_service', 'Out of Service'),
    ], string='Status', default='available')

    code = fields.Char(string=' Code', size=5, required=True)  # Define size as needed
    capacity = fields.Integer(string='Capacity', required=True, 
                              store=True, compute='_compute_unit_capacity', readonly=False,
                             )
    
    description = fields.Text(string='Description', help="Detailed description of the building")


    unit_facility_ids = fields.Many2many(
        'oe.hostel.unit.facility',
        string='Facilities'
    )

    
    # Building Attributes
    location = fields.Char(string='Location')
    building_type = fields.Selection([
        ('hostel', 'Hostel'),
        ('dormitory', 'Dormitory'),
        ('residential', 'Residential'),
    ], string='Building Type')
    

    # Floor Attributes
    
    

    # Room Fields
    room_type = fields.Selection([
        ('single', 'Single'),
        ('double', 'Double'),
        ('triple', 'Triple'),
        ('suite', 'Suite'),
        ('dormitory', 'Dormitory'),
    ], string='Room Type', )


    @api.depends('name', 'unit_id.complete_name', 'unit_type')
    def _compute_complete_name(self):
        for unit in self:
            if unit.unit_id and unit.unit_type != 'building':
                unit.complete_name = '%s/%s' % (unit.unit_id.complete_name, unit.name)
            else:
                unit.complete_name = unit.name

    @api.depends('name', 'unit_id.complete_name', 'unit_type', 'child_ids.capacity')
    def _compute_unit_capacity(self):
        def propagate_capacity_up(unit):
            if unit.unit_type == 'building':
                children_capacity = sum(child.capacity for child in unit.child_ids)
                unit.capacity = children_capacity
            elif unit.unit_type == 'floor':
                children_capacity = sum(child.capacity for child in unit.child_ids if child.unit_type == 'room')
                unit.capacity = children_capacity
            elif unit.unit_type == 'room':
                unit.capacity = unit.room_capacity or 0
    
            if unit.unit_id:
                propagate_capacity_up(unit.unit_id)
    
        for record in self:
            propagate_capacity_up(record)

                
    # Action 
    def action_reserve(self):
        self.write({
            'status': 'reserve',
        })

    def action_out_of_service(self):
        self.write({
            'status': 'out_of_service',
        })
