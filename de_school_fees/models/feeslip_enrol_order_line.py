# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class FeeEnrolOrderLine(models.Model):
    _name = 'oe.feeslip.enrol.order.line'
    _description = 'Enrollment Lines for Feeslip'
    _order = 'sequence, code'

    name = fields.Char(compute='_compute_name', store=True, string='Description', readonly=False)
    feeslip_id = fields.Many2one('oe.feeslip', string='Fee Slip', ondelete='cascade', index=True)
    sequence = fields.Integer(required=True, index=True, default=10)
    code = fields.Char(string='Code')
    amount = fields.Monetary(string='Amount',)
    currency_id = fields.Many2one('res.currency', related='feeslip_id.currency_id')
    amount_residual = fields.Monetary(string='Residual',)
    #order_line_id = fields.Many2one('sale.order.line', string="Order Line")

    #@api.depends('work_entry_type_id')
    def _compute_name(self):
        for record in self:
            record.name = record.name