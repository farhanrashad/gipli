# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    
    is_split_salary = fields.Boolean(string='Salary Split')
    gme_salary = fields.Boolean(string='AEL/GME Salary Split')
    basic_salary = fields.Float(string='Basic Salary')
    house_rent = fields.Float(string='House Rent')
    utility = fields.Float(string='Utility')
    is_medical = fields.Boolean(string='Medical')
    medical_percent = fields.Float(string='Medical (%)', default=10)
    taxable_amount = fields.Float(string='Taxable Amount')
    tax_deduct_amount = fields.Float(string='Tax Deduct Amount')  

    @api.constrains('is_split_salary')
    def _checkis_split_salary(self):
        for contract in self:
            if  contract.is_split_salary==True:
                basic=self.env['basic.salary.devision'].search([('has_category','=','basic')], limit=1)
                house_rent= self.env['basic.salary.devision'].search([('has_category','=','rent')], limit=1)
                utility= self.env['basic.salary.devision'].search([('has_category','=','utility')], limit=1)
                contract.update({
                  'basic_salary':  round(((contract.wage/100)*(basic.percentage if basic else 0))),
                  'house_rent':  round(((contract.wage/100)*(house_rent.percentage if house_rent else 0))),
                  'utility':  round(((contract.wage/100)*(utility.percentage if utility else 0))),
                })
    
    @api.onchange('is_split_salary')
    def onchange_is_split_salary(self):
        for contract in self:
            if  contract.is_split_salary==True:
                basic=self.env['basic.salary.devision'].search([('has_category','=','basic')], limit=1)
                house_rent= self.env['basic.salary.devision'].search([('has_category','=','rent')], limit=1)
                utility= self.env['basic.salary.devision'].search([('has_category','=','utility')], limit=1)
                contract.update({
                    'basic_salary':  round(((contract.wage/100)*(basic.percentage if basic else 0))),
                    'house_rent':  round(((contract.wage/100)*(house_rent.percentage if house_rent else 0))),
                    'utility':  round(((contract.wage/100)*(utility.percentage if utility else 0))),
                })
    
    

