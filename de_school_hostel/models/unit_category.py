# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ProductCategory(models.Model):
    _inherit = "product.category"
    is_hostel = fields.Boolean(default=False)

    def open_products_units(self):
        action = self.env.ref('de_school_hostel.action_product_unit_all').read()[0]
        action.update({
            'name': 'Units',
            'view_mode': 'tree,form',
            'res_model': 'product.template',
            'type': 'ir.actions.act_window',
            'domain': [('is_hostel_unit','=',True)],
            'context': {
                'default_is_hostel_unit': True,
                'search_default_categ_id': self.env.context.get('active_id'),
                'default_categ_id': self.env.context.get('active_id'),
                'group_expand': True,
            },
            
        })
        return action