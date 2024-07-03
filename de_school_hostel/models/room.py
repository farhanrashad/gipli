# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

class HostelBuilding(models.Model):
    _name = 'oe.hostel.building'
    _description = 'Hostel Building'
    _order = 'name'

    active = fields.Boolean(default=True)
    name = fields.Char(string="Building", required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    address_id = fields.Many2one('res.partner', required=True, string="Building Address", domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
        
class HostelBuildingRoom(models.Model):
    _name = 'oe.hostel.room'
    _description = 'Hostel Rooms'
    _parent_name = "room_id"
    _parent_store = True
    _order = 'complete_name, id'
    _rec_name = 'complete_name'
    _rec_names_search = ['complete_name']
    _check_company_auto = True

    
    name = fields.Char(string='Room Name', required=True, index=True, translate=True)
    complete_name = fields.Char("Full Name", compute='_compute_complete_name', recursive=True, store=True)
    room_id = fields.Many2one('oe.hostel.room', 'Parent Room', index=True, 
                              ondelete='cascade', check_company=True,
                              help="The parent room that includes this room.")
    child_ids = fields.One2many('oe.hostel.room', 'room_id', 'Contains')
    parent_path = fields.Char(index=True, unaccent=False)
    room_type = fields.Selection([
        ('building', 'Building'),
        ('floor', 'Floor'),
        ('room', 'Room'),
    ], string='Type',
        default='room', index=True, required=True,
    )

    active = fields.Boolean('Active', default=True, help="By unchecking the active field, you may hide a room without deleting it.")
    company_id = fields.Many2one('res.company', 'Company',
        default=lambda self: self.env.company, index=True,
        help='Let this field empty if this room is shared between companies')



    capacity = fields.Integer(string='Capacity', required=True, default=10)


    @api.depends('name', 'room_id.complete_name', 'room_type')
    def _compute_complete_name(self):
        for room in self:
            if room.room_id and room.room_type != 'building':
                room.complete_name = '%s/%s' % (room.room_id.complete_name, room.name)
            else:
                room.complete_name = room.name