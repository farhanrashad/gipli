from odoo import models, fields, api,_
from datetime import datetime , date, timedelta
from odoo.exceptions import ValidationError, UserError
import calendar



class AttendanceRegister(models.TransientModel):
    _name="oe.school.attend.register.wizard"
    
    # name = 
    school_year_id= fields.Many2one("oe.school.year", string="Year", required=True )
    date_attendance= fields.Datetime(string="Attendance Date", required=True, default=datetime.now())#.replace(hour=23, minute=59, second=59) )
    period_id= fields.Many2one("resource.calendar.attendance", string="Period" )
    course_id= fields.Many2one("oe.school.course", string="Course" )
    subject_id= fields.Many2one("oe.school.course.subject", string="Subject" )
    batch_id= fields.Many2one("oe.school.course.batch", string="Batch" )
    by_period= fields.Boolean('by period',compute="check_attendance_mode" , store= True)
    company_id = fields.Many2one("res.company", string="company", default = lambda self:self.env.company)
    
    @api.depends('company_id.attendance_mode')
    def check_attendance_mode(self):
        for res in self:
            if res.env.company.attendance_mode == 'period':
                res.by_period = True
            else:
                res.by_period = False
                
                
                
    def create_attendance(self):
        try:
            period_id = False
            if self.by_period == True:
                period_id = self.period_id.id
                
            students_obj = self.env['res.partner'].search([('is_student','=',True)])   
            for st in students_obj:
                vals={ 'school_year_id' : self.school_year_id.id,
                       'date_attendance': self.date_attendance,
                       'student_id': st.id,
                       'period_id':period_id,
                       'course_id': self.course_id.id,
                       'subject_id': self.subject_id.id,
                       'batch_id': self.batch_id.id
                       } 
           
                self.env["oe.school.attendance"].create(vals)                     
        except Exception as e:
            print(e.args)   