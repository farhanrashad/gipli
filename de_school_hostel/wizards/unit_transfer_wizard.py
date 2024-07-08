# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError

class TicketReopen(models.TransientModel):
    _name = 'oe.hostel.transfer.unit.wizard'
    _description = 'Ticket Reopen Wizard'

    # Compute Methods
    @api.depends('room_assign_id')
    def _get_default_location_id(self):
        return self.room_assign_id.location_id.id

    
    room_assign_id = fields.Many2one(
        'oe.hostel.room.assign', default=lambda self: self.env.context.get('active_id'))

    src_product_id = fields.Many2one(related='room_assign_id.product_id')
    src_lot_id = fields.Many2one(related='room_assign_id.lot_id')


    location_id = fields.Many2one('stock.location',string='Dormitory',
                                  domain = "[('is_hostel','=',True),('unit_usage','=','internal')]",
                                  store=True, readonly=False,
                                  compute='_compute_location',
                                 )
    product_id = fields.Many2one('product.product', string='Unit',
                                 domain ="[('is_hostel_unit','=',True)]"
                                )
    product_id_tracking = fields.Selection(related='product_id.tracking')
    lot_id = fields.Many2one('stock.lot', string='Sub-Unit',
                                 domain ="[('product_id','=',product_id)]"
                                )

    @api.onchange('room_assign_id')
    @api.depends('room_assign_id')
    def _compute_location(self):
        for record in self:
            record.location_id = record.room_assign_id.location_id.id
            
    def action_transfer(self):
        self._action_picking_return()
        self._action_picking()

    def _action_picking_return(self):
        location_id = self.room_assign_id.location_id.id
        location_dest_id = self.company_id.hostel_location_id.id

        picking_id = self.env['stock.picking'].create(
            self._prepare_picking_values(location_id, location_dest_id, product_id)                                             
        )

    def _action_picking(self):
        location_id = self.room_assign_id.location_id
        location_dest_id = self.company_id.hostel_location_id.id
        
    def _prepare_picking_values(self, location_id, location_dest_id, product_id):
        picking_type_id = self.env.ref('stock.picking_type_internal').id
        picking_values = {
            'picking_type_id': picking_type_id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'scheduled_date': fields.Datetime.now(),
            'partner_id': self.room_assign_id.partner_id.id,
            'state': 'draft',
            'origin': self.room_assign_id.name,
            'room_assign_id': self.room_assign_id.id,
            'move_ids': [(0, 0, {
                'name': self.room_assign_id.name,
                'product_id': self.room_assign_id.product_id.id,
                'product_uom': self.room_assign_id.product_id.uom_id.id,
                'product_uom_qty': 1.0,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'room_assign_id': self.room_assign_id.id,
            })],
            # Add more fields as needed
        }
        return picking_values