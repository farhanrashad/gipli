from odoo import models, fields, api,_
from datetime import datetime , date, timedelta
from odoo.exceptions import ValidationError, UserError


class deAttendanceSettings(models.TransientModel):
    _inherit="res.config.settings"
    
    attendance_mode =  fields.Selection(
        selection=[
            ('subject', "By Subject"),
            ('period', "By Period"),
            ('day', "By day"),
            
       ],
        string="Attendance mode",
     
        default='')
    
    
     
    def set_values(self):
        super(deAttendanceSettings, self).set_values()
        company_id = self.env.user.company_id
        company_id.attendance_mode = self.attendance_mode
        
    
    def get_values(self):
        res = super(deAttendanceSettings, self).get_values()
        res.update(
            attendance_mode = self.env.user.company_id.attendance_mode
           
        )
        return res
        
    
class ResCompanySettings_inh(models.Model):
    _inherit = 'res.company'
    
    
    
    attendance_mode =  fields.Selection(
        selection=[
            ('subject', "By Subject"),
            ('period', "By Period"),
            ('day', "By day"),
            
       ],
        string="Attendance mode",
     
        default='')

    
    

    
   