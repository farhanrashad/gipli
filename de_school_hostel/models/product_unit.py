# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import itertools
import logging
from collections import defaultdict

from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_hostel_unit = fields.Boolean(default=False)

    tracking_serial = fields.Boolean(string='Sub-Units', compute='_compute_tracking_serial', inverse='_inverse_tracking_serial')

    unit_facility_ids = fields.Many2many(
        'oe.hostel.unit.facility',
        string='Facilities',
        domain="[('use_unit','=',True)]"
    )
    sequence_id = fields.Many2one('ir.sequence', related='categ_id.sequence_id')
   
    @api.depends('tracking')
    def _compute_tracking_serial(self):
        for record in self:
            record.tracking_serial = record.tracking == 'serial'

    def _inverse_tracking_serial(self):
        for record in self:
            if record.tracking_serial:
                record.tracking = 'serial'
            else:
                record.tracking = 'none'

    def generate_unit_serial(self):
        return {
            'name': 'Generate Sub-Units',
            'view_mode': 'form',
            'res_model': 'stock.lot.generate.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_open_subunits(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_product_production_lot_form")
        product_id = self.env['product.product'].search([('product_tmpl_id','=',self.id)],limit=1)
        action['domain'] = [('product_id', 'in', self.product_variant_ids.ids)]
        action['context'] = {
            'default_product_id': product_id.id,
            'default_company_id': (self.company_id or self.env.company).id,
        }
        
        return action