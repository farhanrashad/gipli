from odoo import api, fields, models,_
from odoo.exceptions import UserError

class Attendance(models.Model):

    _inherit = 'hr.attendance'
    
    attendance_date = fields.Date('Attendance Date')
    
    
    @api.onchange('check_in')
    def set_check_in(self):
        for rec in self:
            if rec.check_in:
                rec.attendance_date = rec.check_in
