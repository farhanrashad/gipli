# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'
    
    is_customer = fields.Boolean("Is Customer")
    is_supplier = fields.Boolean("Is Vendor")
    
    # update customer /vendor field based on res partner search mode
    @api.model
    def create(self, vals):
        res = super().create(vals)
        if vals.get('is_company')==False and vals.get('company_id')!=False:
            if res.parent_id.is_customer == True:
                res.write({'customer_rank':1,'is_customer':True})
            else:
                res.write({'customer_rank':0,'is_customer':False})
            
            if res.parent_id.is_supplier == True:
                res.write({'supplier_rank':1,'is_supplier':True})
            else:
                res.write({'supplier_rank':0,'is_supplier':False})
        else:
            if vals.get('is_customer')==True:
                res.write({'customer_rank':1})
            elif vals.get('is_customer')==False:
                res.write({'customer_rank':0})
                
            if vals.get('is_supplier')==True:
                res.write({'supplier_rank':1})
            elif vals.get('is_supplier')==False:
                res.write({'supplier_rank':0})
        return res
    
    def write(self, vals):
        res = None
        if vals.get('is_customer')==True:
            vals.update({'customer_rank':1})
            res = super(Partner,self).write(vals)
            if self.child_ids:
                self.child_ids.write({'customer_rank':1,'is_customer':True})
        elif vals.get('is_customer')==False:
            vals.update({'customer_rank':0})
            res = super(Partner,self).write(vals)
            if self.child_ids:
                self.child_ids.write({'customer_rank':0,'is_customer':False})
            
        if vals.get('is_supplier')==True:
            vals.update({'supplier_rank':1})
            res = super(Partner,self).write(vals)
            if self.child_ids:
                self.child_ids.write({'supplier_rank':1,'is_supplier':True})
        elif vals.get('is_supplier')==False:
            vals.update({'supplier_rank':0})
            res = super(Partner,self).write(vals)
            if self.child_ids:
                self.child_ids.write({'supplier_rank':0,'is_supplier':False})
        if res==None:
            res = super(Partner,self).write(vals)
        return res