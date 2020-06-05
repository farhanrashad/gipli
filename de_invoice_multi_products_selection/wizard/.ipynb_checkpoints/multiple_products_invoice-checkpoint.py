# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MultipleInvoiceProducts(models.TransientModel):
    _name = "account.multiple.products"

    product_ids = fields.Many2many('product.product',string="Products")

    def add_multiple_products(self):
        move_line_obj = self.env['account.move.line']  
        if self.env.context.get('active_model')=='account.move': 
            active_id = self.env.context.get('active_id',False)
            move_id = self.env['account.move'].search([('id', '=', active_id)]) 
            if move_id and self.product_ids: 
                for record in self.product_ids:
                    if record:
                        tax_list = []  
                        for tax in record.taxes_id:
                            if tax:
                                tax_line = self.env['account.tax'].search([('id','=',tax.id)]) 
                                if tax_line:
                                    tax_list.append(tax.id)               
                        move_line_dict ={
                                  'move_id':move_id.id,
                                  'product_id':record.id,
                                  'product_uom_id':record.uom_id.id, 
                                  'price_unit':record.standard_price,  
                                  'quantity':1.00,
                                  'name':record.name,
                                'account_id':record.categ_id.property_account_income_categ_id.id,
                                  'tax_ids':[(6,0,tax_list)]
                                  }          
                        move_line_obj.create(move_line_dict)
