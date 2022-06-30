# -*- coding: utf-8 -*-   
    
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EmployeeReportWizard(models.TransientModel):
    _name = "employee.statement.wizard"
    _description = 'Employee Statment Wizard'
    
    on_date =  fields.Date(string='From Date', )
    date_to =  fields.Date(string='To Date', )
    
    
    def check_report(self):
        data = {
            'on_date': self.on_date,
            'date_to': self.date_to,
            
        }
            
        return self.env.ref('de_employee_statement.hr_employee_statement_report_xlsx').report_action(self, data=data)
