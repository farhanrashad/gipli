from odoo import models, fields, api,_
from datetime import datetime
from odoo.exceptions import ValidationError, UserError
class WizShifAlloc(models.TransientModel):
    _name = 'wizard.shift.alloc'
    
    shift_id = fields.Many2one('shift.type',string = 'Shift Type')
    date_from = fields.Date(string='Date From', required=True, default=datetime.today())
    date_to = fields.Date(string='Date To', required=True, default=datetime.today())
    employee_ids = fields.Many2many('hr.employee', string= "Employee")
    description = fields.Text(string ="Text")
    