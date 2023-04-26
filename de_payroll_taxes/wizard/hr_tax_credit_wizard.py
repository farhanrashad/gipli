# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

class HrTaxCreditWizard(models.TransientModel):
    _name = 'hr.tax.credit.wizard'
    _description='Tax Credit Wizard'
    
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date = fields.Date(string='Start Date', required=True, default=fields.date.today() )
    credit_amount = fields.Float(string='Credit Amount')
    number_of_month = fields.Integer(string='Number Of Month', default=1)
    remarks = fields.Char(string='Remarks')
    credit_type_id = fields.Many2one('tax.credit.type', string='Tax Credit Type', required=True)

    
    def action_create_tax_credit(self):
        for line in self:
            period=line.date
            count = 0
            for ext_rang in range(self.number_of_month):
                count +=1
                if count > 1:
                    period=period+timedelta(31)
                vals={
                    'name': line.employee_id.name +' ('+str(line.employee_id.emp_number)+')',
                    'employee_id': line.employee_id.id,
                    'date': period,
                    'fiscal_month': period.month,
                    'tax_year': period.year,
                    'tax_amount': (line.credit_amount/line.number_of_month),
                    'company_id': line.employee_id.company_id.id,
                    'remarks': line.remarks,
                    'dist_month': line.number_of_month,
                    'post': 'N',
                    'credit_type_id': line.credit_type_id.id,
                }
                tax_credit=self.env['hr.tax.credit'].create(vals)
    
    
    
    
    
    
 
    
    
    

