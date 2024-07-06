# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ProductCategory(models.Model):
    _inherit = "product.category"
    is_hostel = fields.Boolean(default=False)

    sequence_code = fields.Char(string='Code', size=5, required=True)
    sequence_id = fields.Many2one('ir.sequence', string='Sequence', readonly=True)


    # CRUD
    @api.model
    def create(self, vals):
        category = super(ProductCategory, self).create(vals)
        if 'sequence_code' in vals and vals['sequence_code']:
            category._create_sequence(vals['sequence_code'])
        return category

    def write(self, vals):
        result = super(ProductCategory, self).write(vals)
        if 'sequence_code' in vals and vals['sequence_code']:
            for category in self:
                category._create_sequence(vals['sequence_code'])
        return result

    def _create_sequence(self, sequence_code):
        for category in self:
            if not category.sequence_id:
                sequence = self.env['ir.sequence'].create({
                    'name': '%s Sequence' % category.name,
                    'prefix': sequence_code,
                    'padding': 5,
                    'implementation': 'no_gap',
                    'code': 'product.category.sequence.%s' % sequence_code,
                })
                category.sequence_id = sequence
                
    # Actions
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