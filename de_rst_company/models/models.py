# -*- coding: utf-8 -*-

from odoo import models, fields, api


# class de_rst_company(models.Model):
#    _inherit='res.users'
#
#    current_comp= fields.Many2one('res.company',string= "current company",  default=lambda self: self.env.company.id)
   
   
class SalecompDomain(models.Model):
    _inherit="sale.order"
    
    @api.onchange('company_id')
    def getCompDom(self):
        if self.env.company.name == 'GMSA ENERGY (PVT) LTD':
            comp_id= self.env['res.company'].search([('name','=','GMSA ENERGY (PVT) LTD')])
            recs= self.env['res.partner'].sudo().search([('company_id','=',comp_id.id)])
            if recs:  
                return {'domain' : {'partner_id' : [('id', 'in', recs.ids)]}} 
 
 
 
 
class SaleOrdercompDomain(models.Model):
    _inherit="sale.order.line"
    
    @api.onchange('company_id')
    def getCompDom(self):
        if self.env.company.name == 'GMSA ENERGY (PVT) LTD':
            comp_id= self.env['res.company'].search([('name','=','GMSA ENERGY (PVT) LTD')])
            recs= self.env['product.product'].sudo().search([('company_id','=',comp_id.id)])
            if recs:  
                return {'domain' : {'product_id' : [('id', 'in', recs.ids)]}}     




class AccCompDomain(models.Model):
    _inherit="account.move"
    
    @api.onchange('company_id')
    def getCompDom(self):
        if self.env.company.name == 'GMSA ENERGY (PVT) LTD':
            comp_id= self.env['res.company'].search([('name','=','GMSA ENERGY (PVT) LTD')])
            recs= self.env['res.partner'].sudo().search([('company_id','=',comp_id.id)])
            if recs:  
                return {'domain' : {'partner_id' : [('id', 'in', recs.ids)]}} 
 
 
 
 
class AccMoveLineCompDomain(models.Model):
    _inherit="account.move.line"
    
    @api.onchange('company_id')
    def getCompDom(self):
        if self.env.company.name == 'GMSA ENERGY (PVT) LTD':
            comp_id= self.env['res.company'].search([('name','=','GMSA ENERGY (PVT) LTD')])
            recs= self.env['product.product'].sudo().search([('company_id','=',comp_id.id)])
            if recs:  
                return {'domain' : {'product_id' : [('id', 'in', recs.ids)]}}     
            
            
    @api.onchange('company_id')
    def getCompDompartner(self):
        if self.env.company.name == 'GMSA ENERGY (PVT) LTD':
            comp_id= self.env['res.company'].search([('name','=','GMSA ENERGY (PVT) LTD')])
            recs= self.env['res.partner'].sudo().search([('company_id','=',comp_id.id)])
            if recs:  
                return {'domain' : {'partner_id' : [('id', 'in', recs.ids)]}} 
    