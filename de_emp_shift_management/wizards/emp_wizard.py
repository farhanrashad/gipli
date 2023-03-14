from odoo import models, fields, api,_
from datetime import datetime
from odoo.exceptions import ValidationError, UserError
class WizShifAlloc(models.TransientModel):
    _name = 'wizard.shift.alloc'
    
    
    shift_id = fields.Many2one("emp.shift", string = "Shift")
    shift_type_id = fields.Many2one('shift.type',string = 'Shift Type')
    date_from = fields.Date(string='Date From', required=True, default=datetime.today())
    date_to = fields.Date(string='Date To', required=True, default=datetime.today())
    employee_ids = fields.Many2many('hr.employee', string= "Employee")
    description = fields.Text(string ="Text")
    
    
    def create_shifts(self):
        for emp in self.employee_ids:
            rec = self.env['employee.shift.alloc'].create({
                'shift_id': self.shift_id.id,
                'shift_type_id': self.shift_type_id.id,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'state': 'done',
                'employee_id':emp.id 
            })
    
            print(rec)
        
        
        
        