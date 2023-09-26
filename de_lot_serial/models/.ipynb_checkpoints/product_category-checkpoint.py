# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class ProductCategory(models.Model):
    _inherit = "product.category"
    
    
    #sequence_ids = fields.Many2many('ir.sequence', 'Sequence', copy=False)
    sequence_ids = fields.Many2many('ir.sequence', 'product_category_sequence_rel', 'product_category_sequence_id',
        'sequence_id', string='Sequences')

    
    
