# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    roll = fields.Char(string='Roll')
    pcs = fields.Char(string='PCS')
    weight_price = fields.Float(string='Weight Price', domain=[('parnter_id', 'in', 'CONE')])
    subtotal_weight = fields.Monetary(compute='_compute_amount_t', string='Subtotal')
    
    @api.depends('subtotal_weight','weight_price', 'demand_qty')    
    def _compute_amount_t(self):
        for line in self:
            line.subtotal_weight = line.weight_price * line.demand_qty