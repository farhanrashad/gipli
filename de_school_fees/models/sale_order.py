# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError

class SaleOrder(models.Model):
    _inherit= 'sale.order'

    fee_struct_id = fields.Many2one(
        'oe.fee.struct', string='Fee Structure',
        compute='_compute_struct_id', 
        )

    def _compute_struct_id(self):
        for order in self:
            struct_id = self.env['oe.fee.struct'].search([
                ('active','=',True),
                '|',
                ('course_id','=',order.course_id.id),
                ('course_id','=',False),
            ],limit=1)
            order.fee_struct_id = struct_id.id