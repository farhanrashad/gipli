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
        new_room_assign_id = self._action_transfer()
        self._action_picking_return()
        self.room_assign_id._action_open_transfer(new_room_assign_id)

    def _action_transfer(self):
        new_room_assign_id = self.env['oe.hostel.room.assign'].create(self._prepare_room_assignment())
        self.room_assign_id.write({
            'room_assign_id': new_room_assign_id.id,
            'state': 'cancel'
        })
        new_room_assign_id.action_confirm()
        new_room_assign_id.action_validate()
        return new_room_assign_id
        
    def _action_picking_return(self):
        
        location_id = self.room_assign_id.location_id.id
        location_dest_id = self.room_assign_id.company_id.hostel_location_id.id

        old_picking_id = self.room_assign_id.assign_picking_ids.filtered(lambda x:x.state == 'done')
        picking_id = self.env['stock.picking'].create(
            self._prepare_picking_values(location_id, location_dest_id, self.src_product_id)
        )
        picking_id.sudo().action_confirm()
        for move in picking_id.move_ids:
            self.env['stock.move.line'].create(self.room_assign_id._prepare_stock_move_line(move))
        picking_id.sudo().button_validate()

        for pk in old_picking_id:
            pk.write({
                'return_id': picking_id.id,
            })
        


    def _prepare_room_assignment(self):
        return {
            'partner_id': self.room_assign_id.partner_id.id,
            'location_id': self.location_id.id,
            'product_id': self.product_id.id,
            'lot_id': self.lot_id.id,
            'date_order': fields.Datetime.today(),
            'date_start': fields.Datetime.today(),
            'duration': self.room_assign_id.duration,
            'date_end': self.room_assign_id.date_end,
            'company_id': self.room_assign_id.company_id.id,
            'state': 'draft',
            #'room_assign_id': self.room_assign_id.id,
        }

    
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