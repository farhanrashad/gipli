# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models,fields,api,_

class ShProductTemplate(models.Model):
    _inherit='product.template'
    
    sh_retail_price = fields.Float("Retail Price")
    is_tax_retail = fields.Boolean('Taxes on Retail Price')
    
class ShProductProduct(models.Model):
    _inherit='product.product'
    
    sh_retail_price = fields.Float("Retail Price")