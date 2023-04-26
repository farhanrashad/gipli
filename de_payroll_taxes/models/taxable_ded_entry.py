# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TaxableDedEntry(models.Model):
    _name = 'taxable.ded.entry'
    _description = 'Taxable Ded Entry'
    _rec_name = 'employee_id'
    
    
    
    remarks = fields.Char(string='Remarks')
    amount = fields.Float(string='Amount', required=True)
    post = fields.Boolean(string='Posted')
    date  = fields.Date(string='Date', default=fields.date.today().replace(day=1))
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    company_id = fields.Many2one('res.company', string='Company', compute='_compute_company')
    
    @api.depends('employee_id')
    def _compute_company(self):
        for line in self:
            if line.employee_id:
                line.update({
                    'company_id': line.employee_id.company_id.id,
                })
            else:
                line.update({
                    'company_id': self.env.company,
                })
        
    
    
    
    
    
    

