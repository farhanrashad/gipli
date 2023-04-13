from odoo import models, fields, api,_
from datetime import datetime
from odoo.exceptions import ValidationError, UserError

class WizEmployeeShifts(models.TransientModel):
    _name = 'wizard.report.emp.shift'
    
    date_from = fields.Date(string='Date From', required=True, default=datetime.today())
    date_to = fields.Date(string='Date To', required=True, default=datetime.today())
    
    
    def get_emp_pdf_report(self):
        data = {
            'model': 'wizard.report.emp.shift',
            'ids': self.ids,
            'form': {
                'date_from': self.date_from, 'date_to': self.date_to,
            },
        }

        # ref `module_name.report_id` as reference.
        return self.env.ref('de_emp_shift_management.action_report_emp_shift_pdf').report_action(self, data=data)

        
    def get_emp_xlsx_report(self):
        
        data = {
            'model': 'wizard.report.emp.shift',
            'ids': self.ids,
            'form': {
                'date_from': self.date_from, 'date_to': self.date_to,
            },
        }

        # ref `module_name.report_id` as reference.
        return self.env.ref('de_emp_shift_management.action_report_emp_shift_xlsx').report_action(self, data=data)  
        
        
        
        