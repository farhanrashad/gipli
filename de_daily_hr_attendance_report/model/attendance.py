from odoo import api, fields, models,_
from odoo.exceptions import UserError

class Attendance(models.Model):

    _inherit = 'hr.attendance'
    
    attendance_date = fields.Date('Attendance Date')
    
