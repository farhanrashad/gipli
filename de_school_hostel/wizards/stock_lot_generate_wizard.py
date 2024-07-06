# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models

class GenerateLotWizard(models.TransientModel):
    _name = "stock.lot.generate.wizard"
    _description = "Lot Generation Wizard"
    
    product_tmpl_id = fields.Many2one('product.template', string='Unit',
                                     default=lambda self: self.env.context.get('active_id'),
                                     )
    quantity = fields.Integer(string='Quantity', default=1)
    
    
    def _get_category_sequence(self):
        for record in self:
            record.category_sequence_id = record.product_tmpl_id.categ_id.sequence_id.id
        
    def generate_serial(self):
        product_ids = self.env['product.product'].search([('product_tmpl_id','=',self.product_tmpl_id.id)])
        for product in product_ids:
            for x in range(self.quantity):
                if self.product_tmpl_id.categ_id.sequence_id:
                    self.env['stock.lot'].sudo().create({
                        'product_id': product.id,
                        'name': self.product_tmpl_id.categ_id.sequence_id.next_by_id(),
                        'company_id': self.env.user.company_id.id,
                    })
                
            
        
    
    