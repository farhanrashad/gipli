from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    _description = "Sale Order"

    partner_id = fields.Many2one(string="Student", domain=[('is_hostel_room', '=', True)])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Un Assign'),
        ('sale', 'Assign'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft',
        track_visibility='onchange')
    date_start = fields.Datetime(string='Date Start', required=True)
    date_end = fields.Datetime(string='Date End', required=True)
    product_id = fields.Many2one('product.product', string='Room', required=True)
    lot_id = fields.Many2one('stock.lot', string='Room No', required=True)

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_end and record.date_start >= record.date_end:
                raise ValidationError("End date must be greater than start date!")

    @api.constrains('room_rent_status')
    def _check_room_rent_status(self):
        for order in self:
            if order.room_rent_status == 'rented' and not order.date_start:
                raise ValueError("Start date is required for rented rooms")

    # def create_delivery_and_transfer(self):
    #     # Get the delivery and picking types
    #     delivery_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)
    #     internal_transfer_type = self.env['stock.picking.type'].search([('code', '=', 'internal')], limit=1)
    #
    #     # Create the delivery
    #     delivery_vals = {
    #         'partner_id': self.partner_id.id,
    #         'origin': self.name,
    #         'picking_type_id': delivery_type.id,
    #     }
    #     delivery = self.env['stock.picking'].create(delivery_vals)
    #
    #     # Create the move
    #     move_vals = {
    #         'name': self.product_id.name,
    #         'product_id': self.product_id.id,
    #         'product_uom_qty': 1,
    #         'product_uom': self.product_id.uom_id.id,
    #         'picking_id': delivery.id,
    #         'location_id': delivery_type.default_location_src_id.id,
    #         'location_dest_id': delivery_type.default_location_dest_id.id,
    #         'lot_id': self.lot_id.id,
    #     }
    #     move = self.env['stock.move'].create(move_vals)
    #
    #     # Create the internal transfer
    #     transfer_vals = {
    #         'name': self.name + ' Transfer',
    #         'picking_type_id': internal_transfer_type.id,
    #         'location_id': delivery_type.default_location_dest_id.id,
    #         'location_dest_id': internal_transfer_type.default_location_dest_id.id,
    #     }
    #     transfer = self.env['stock.picking'].create(transfer_vals)
    #
    #     # Create the move
    #     transfer_move_vals = {
    #         'name': self.product_id.name,
    #         'product_id': self.product_id.id,
    #         'product_uom_qty': 1,
    #         'product_uom': self.product_id.uom_id.id,
    #         'picking_id': transfer.id,
    #         'location_id': internal_transfer_type.default_location_src_id.id,
    #         'location_dest_id': internal_transfer_type.default_location_dest_id.id,
    #         'lot_id': self.lot_id.id,
    #     }
    #     transfer_move = self.env['stock.move'].create(transfer_move_vals)
    #
    #     # Validate the delivery and internal transfer
    #     delivery.action_assign()
    #     delivery.action_done()
    #     transfer.action_assign()
    #     transfer.action_done()
    #
    #     return True

    def action_confirm(self):
        res = super(SaleOrderInherit, self).action_confirm()
        # Create and validate delivery
        for order in self:
            order.picking_ids.action_confirm()
            for picking in order.picking_ids:
                for move in picking.move_lines:
                    move.write({'lot_id': order.lot_id.id})
                    move.action_assign()
            order.create_delivery_and_transfer()
        return res
