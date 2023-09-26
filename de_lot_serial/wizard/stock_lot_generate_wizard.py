# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round


class GenerateLotWizard(models.TransientModel):
    _name = "stock.lot.generate.wizard"
    _description = "Lot Generation Wizard"
    
    product_tmpl_id = fields.Many2one('product.template', string='Product Template')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Integer(string='Quantity', default=1)
    sequence_id = fields.Many2one('ir.sequence', 'Sequence', copy=False)
    category_sequence_ids = fields.Many2many('ir.sequence')
    
    @api.model
    def default_get(self, fields):
        res = super(GenerateLotWizard, self).default_get(fields)
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'product.template':
            product_template = self.env['product.product'].browse(self.env.context.get('active_id'))
            product = self.env['product.product'].search([('product_tmpl_id','=',product_template.id)],limit=1)
            if product.exists():
                res.update({
                    'product_tmpl_id': product_template.id,
                    'product_id': product.id,
                    'category_sequence_ids': product.categ_id.sequence_ids
                })
        elif self.env.context.get('active_id') and self.env.context.get('active_model') == 'product.product':
            product = self.env['product.product'].browse(self.env.context.get('active_id'))
            if product.exists():
                res.update({
                    'product_id': product.id,
                    'category_sequence_ids': product.categ_id.sequence_ids
                })
        return res
    
    def _get_category_sequence(self):
        for record in self:
            record.category_sequence_ids = record.product_id.categ_id.sequence_ids.ids
        
    def generate_serial(self):
        for x in range(self.quantity):
            if self.sequence_id.id:
                self.env['stock.production.lot'].sudo().create({
                    'product_id': self.product_id.id,
                    'name': self.sequence_id.next_by_id(),
                    'company_id': self.env.user.company_id.id,
                })
                
            
        
    
    