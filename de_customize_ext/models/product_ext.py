# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import AccessError, UserError
import datetime
from datetime import date, datetime


class ProductTemplateExt(models.Model):
    _inherit = 'product.template'

    activate_production = fields.Boolean(string='Activate Contractual Production')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', required=True)


class AccountInvoiceExt(models.Model):
    _inherit = 'account.invoice'

    de_production_id = fields.Many2many(comodel_name='mrp.production', string='Production Id')


class MrpBomLineExt(models.Model):
    _inherit = 'mrp.bom.line'

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
            if self.product_id.activate_production == True:
                self.wage_price = self.product_id.list_price

    wage_price = fields.Float(string='Wage Price')


class MrpProductionExt(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def post_inventory(self):
        for order in self:
            print('yaseeeeeeeeeeen')
            moves_not_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done')
            moves_to_do = order.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            for move in moves_to_do.filtered(lambda m: m.product_qty == 0.0 and m.quantity_done > 0):
                move.product_uom_qty = move.quantity_done
            moves_to_do._action_done()
            moves_to_do = order.move_raw_ids.filtered(lambda x: x.state == 'done') - moves_not_to_do
            order._cal_price(moves_to_do)
            moves_to_finish = order.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            moves_to_finish._action_done()
            order.action_assign()
            consume_move_lines = moves_to_do.mapped('active_move_line_ids')
            for moveline in moves_to_finish.mapped('active_move_line_ids'):
                if moveline.product_id == order.product_id and moveline.move_id.has_tracking != 'none':
                    if any([not ml.lot_produced_id for ml in consume_move_lines]):
                        raise UserError(_('You can not consume without telling for which lot you consumed it'))
                    # Link all movelines in the consumed with same lot_produced_id false or the correct lot_produced_id
                    filtered_lines = consume_move_lines.filtered(lambda x: x.lot_produced_id == moveline.lot_id)
                    moveline.write({'consume_line_ids': [(6, 0, [x for x in filtered_lines.ids])]})
                else:
                    # Link with everything
                    moveline.write({'consume_line_ids': [(6, 0, [x for x in consume_move_lines.ids])]})
            production_lines = self.env['stock.move'].search(['&', ('raw_material_production_id', '=', order.id), ('state', '=', 'done')])
            for prod in production_lines:
                if prod.product_id.activate_production == True:
                    existing_bill = self.env['account.invoice'].search(['&', ('partner_id', '=', prod.product_id.partner_id.id), ('state', '=', 'draft')])
                    existing_bill_lines = self.env['account.invoice.line'].search([('invoice_id', '=', existing_bill.id)])
                    if existing_bill:
                        self.env['account.invoice.line'].create({
                            'invoice_id': existing_bill.id,
                            'product_id': prod.product_id.id,
                            'name': 'Production Product',
                            'quantity': prod.quantity_done,
                            'account_id': 17,
                            'price_unit': prod.product_id.list_price,
                            })
                    else:
                        journal = self.env['account.journal'].search([('name', '=', 'Vendor Bills')])
                        supplier_line = {
                            'product_id': prod.product_id.id,
                            'name': 'Production Product',
                            'quantity': prod.quantity_done,
                            'account_id': 17,
                            'price_unit': prod.product_id.list_price,
                        }
                        record_line = {
                            'reference': order.name,
                            'partner_id': prod.product_id.partner_id.id,
                            'date_invoice': fields.Date.today(),
                            'date_due': date.today(),
                            'type': 'in_invoice',
                            'journal_id': journal.id,
                            'invoice_line_ids': [(0, 0, supplier_line)],
                        }
                        record = self.env['account.invoice'].create(record_line)
                    # rec.bill_generated = 'true'
        return True

