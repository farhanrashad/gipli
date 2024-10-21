# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Saritha Sahadevan @cybrosys(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo.exceptions import UserError
from odoo import models, fields, api, _


class InvoiceStockMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _default_picking_receive(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)], limit=1)
        if not types:
            types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        return types[:1]

    @api.model
    def _default_picking_transfer(self):
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'outgoing'), ('warehouse_id.company_id', '=', company_id)], limit=1)
        if not types:
            types = type_obj.search([('code', '=', 'outgoing'), ('warehouse_id', '=', False)])
        return types[:4]

    @api.model
    def _default_picking_type(self):
        # Check the type of the invoice and apply logic based on that
        if self.type in ['out_invoice', 'in_refund']:
            # If out_invoice or in_refund, get outgoing picking type
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'outgoing'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
        elif self.type in ['in_invoice', 'out_refund']:
            # If in_invoice or out_refund, get incoming picking type
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'incoming'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
        else:
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'internal'),
                ('company_id', '=', self.company_id.id)
            ], order="id desc", limit=1)

        # Return the found picking type, or False if not found
        return picking_type if picking_type else False

	

    picking_count = fields.Integer(string="Count")
    invoice_picking_id = fields.Many2one('stock.picking', string="Picking Id")
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type', 
                                      compute='_compute_picking_type_id',
                                      readonly=False,
                                      store=True,
                                      help="This will determine picking type of incoming shipment")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('proforma', 'Pro-forma'),
        ('proforma2', 'Pro-forma'),
        ('posted', 'Posted'),
        ('post', 'Post'),
        ('cancel', 'Cancelled'),
        ('done', 'Received'),
    ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)

    @api.depends('type', 'company_id')  # Depends on the type of invoice and the company
    def _compute_picking_type_id(self):
        for order in self:
            if order.type in ['out_invoice', 'in_refund']:
                # If out_invoice or in_refund, get outgoing picking type
                picking_type = self.env['stock.picking.type'].search([
                    ('code', '=', 'outgoing'),
                    ('company_id', '=', order.company_id.id)
                ], limit=1)
            elif order.type in ['in_invoice', 'out_refund']:
                # If in_invoice or out_refund, get incoming picking type
                picking_type = self.env['stock.picking.type'].search([
                    ('code', '=', 'incoming'),
                    ('company_id', '=', order.company_id.id)
                ], limit=1)
            else:
                # Fallback to 'Receipts' picking type for unexpected types
                picking_type = self.env['stock.picking.type'].search([
                    ('code', '=', 'internal'),
                    ('company_id', '=', order.company_id.id)
                ], order="id desc", limit=1)

            # Set the computed picking_type_id or False if no picking type found
            order.picking_type_id = picking_type if picking_type else False

        
    def action_stock_move(self):
        for order in self:
            # Determine the destination location based on the picking type
            if order.picking_type_id.code == 'outgoing':
                location_id = order.picking_type_id.default_location_src_id
                location_dest_id = self.env['stock.location'].search([
                    ('usage', '=', 'customer'),
                    ('active', '=', True),
                    '|',  # Logical OR for company_id condition
                    ('company_id', '=', order.company_id.id),
                    ('company_id', '=', False)
                ], limit=1)
            elif order.picking_type_id.code == 'incoming':
                location_id = self.env['stock.location'].search([
                    ('usage', '=', 'supplier'),
                    ('active', '=', True),
                    '|',  # Logical OR for company_id condition
                    ('company_id', '=', order.company_id.id),
                    ('company_id', '=', False)
                ], limit=1)
                location_dest_id = order.picking_type_id.default_location_dest_id
            else:
                location_id = order.picking_type_id.default_location_src_id
                location_dest_id = order.picking_type_id.location_dest_id

            if not order.picking_type_id:
                raise UserError("Picking Type not found")
                
            # Check if location was found, raise an error if not
            if not location_dest_id:
                raise UserError(_("Destination location not found for the picking type: %s") % order.picking_type_id.code)

            # Proceed with picking creation if no previous picking exists
            if not order.invoice_picking_id:
                # Prepare the picking data
                pick = {
                    'picking_type_id': order.picking_type_id.id,
                    'partner_id': order.partner_id.id,
                    'origin': order.name,
                    'location_dest_id': location_dest_id.id,
                    'location_id': location_id.id
                }

                # Create the picking
                picking = self.env['stock.picking'].create(pick)

                # Link the picking to the order
                order.invoice_picking_id = picking.id

                # Update the picking count (for current order or total count)
                order.picking_count = len(order.invoice_picking_id)

                # Create stock moves for valid invoice lines
                moves = order.invoice_line_ids.filtered(
                    lambda r: r.product_id.type in ['product', 'consu']
                )._create_stock_moves(picking)

                # Confirm and assign the stock moves
                move_ids = moves._action_confirm()
                move_ids._action_assign()

    def action_view_picking(self):
        action = self.env.ref('stock.action_picking_tree_ready')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        result['domain'] = [('id', '=', self.invoice_picking_id.id)]
        pick_ids = sum([self.invoice_picking_id.id])
        if pick_ids:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids or False
        return result


class SupplierInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            price_unit = line.price_unit
            template = {
                'name': line.name or '',
                'product_id': line.product_id.id,
                'product_uom': line.product_uom_id.id,
                'location_id': picking.location_id.id,
                'location_dest_id': picking.location_dest_id.id,
                'picking_id': picking.id,
                # 'move_dest_id': False,
                'state': 'draft',
                'company_id': line.move_id.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': picking.picking_type_id.id,
                # 'procurement_id': False,
                'route_ids': 1 and [
                    (6, 0, [x.id for x in self.env['stock.location.route'].search([('id', 'in', (2, 3))])])] or [],
                'warehouse_id': picking.picking_type_id.warehouse_id.id,
            }
            print(template['route_ids'], "two")
            diff_quantity = line.quantity
            tmp = template.copy()
            tmp.update({
                'product_uom_qty': diff_quantity,
            })
            template['product_uom_qty'] = diff_quantity
            done += moves.create(template)
        return done
