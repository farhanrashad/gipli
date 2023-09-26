from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    lot_automation = fields.Char(string='Lot Automation', compute='_compute_lot_automation')

    @api.depends('type','tracking','product_variant_ids','product_variant_count')
    def _compute_lot_automation(self):
        mode = ''
        for product in self:
            if len(product.categ_id.sequence_ids):
                if product.product_variant_count > 1:
                    mode = 'product'
                else:
                    mode = 'template'
            else:
                mode = 'none'
            product.lot_automation = mode + '_' + product.tracking
