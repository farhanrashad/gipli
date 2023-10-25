from odoo import models, fields, api,tools, _
from datetime import datetime , date, timedelta
from odoo.exceptions import ValidationError, UserError
import calendar



class WizardReportAttendanceDetails(models.TransientModel):
    _name="oe.school.attend.report.wizard"
    
    period_id= fields.Many2one("resource.calendar.attendance", string="Period" )
    course_id= fields.Many2one("oe.school.course", string="Course" )
    subject_id= fields.Many2one("oe.school.course.subject", string="Subject" )
    batch_id= fields.Many2one("oe.school.course.batch", string="Batch" )
    by_period= fields.Boolean('by period',compute="check_attendance_mode" , store= True)
  
    date_from = fields.Date(string= "Date from")
    date_to = fields.Date(string= "Date to")
    status_attendance =fields.Selection( selection=[
           
            ('present', "Present"),
            ('absent', "Absent"),
            
       ],
        string="Status",)
    is_late= fields.Boolean(string="Late", default=False)
    company_id = fields.Many2one("res.company", string="company", default = lambda self:self.env.company)
    
    
    
    
    @api.depends('company_id.attendance_mode')
    def check_attendance_mode(self):
        for res in self:
            if res.env.company.attendance_mode == 'period':
                res.by_period = True
            else:
                res.by_period = False
                
    def print_attendance_details(self):
        # return self.env["oe.school.dynamic.report"].with_context(date_from = self.date_from ,date_to = self.date_to).init()
    
        return self.env["oe.school.dynamic.report"].get_ReportVals(date_from = self.date_from 
                                                          ,date_to = self.date_to,
                                                           period_id = self.period_id,
                                                           course_id = self.course_id,
                                                           subject_id = self.subject_id,
                                                           batch_id = self.batch_id,
                                                           status_attendance = self.status_attendance,
                                                           is_late=self.is_late
                                                           )
        
class AttendanceDynamicReports(models.Model):
    _name="oe.school.dynamic.report"
    _auto = False 
    # _description = 'Attendance Detail report'
    # _order = 'date'
 
    
    date =fields.Date(string="Attendance date")
    partner_id = fields.Many2one("res.partner",string="Student")        
    course_id= fields.Many2one("oe.school.course", string="Course" )
    subject_id= fields.Many2one("oe.school.course.subject", string="Subject" )
    batch_id= fields.Many2one("oe.school.course.batch", string="Batch" )          
    status_attendance =fields.Selection( selection=[
           
            ('present', "Present"),
            ('absent', "Absent"),
            
       ],
        string="Status",)
    is_late= fields.Boolean(string="Late", default=False)
    

    def get_ReportVals(self, **kwargs):
        if kwargs != {}:
            date_from =kwargs['date_from'].strftime("%Y%m%d")
            date_to =kwargs['date_to'].strftime("%Y%m%d")
            period_id = kwargs['period_id']
            course_id = kwargs['course_id']
            subject_id = kwargs['subject_id']
            batch_id = kwargs['batch_id']
            status_attendance = kwargs['status_attendance']
            is_late=kwargs['is_late']
  
            tools.drop_view_if_exists(self.env.cr, 'oe_school_dynamic_report')
            where_string =f""" WHERE CAST(a.date_attendance as DATE) >= CAST({date_from} AS varchar(20))::DATE
                               AND CAST(a.date_attendance as DATE) <= CAST({date_to} AS varchar(20))::DATE
                               AND a.is_late = {is_late}"""
                              
            if period_id:
                where_string +=f" AND a.period_id = {period_id.id}"                 
                              
            if course_id:
                where_string +=f" AND a.course_id = {course_id.id}" 
                
            if subject_id:
                where_string +=f" AND a.subject_id = {subject_id.id}"     
                
            if batch_id:
                where_string +=f" AND a.batch_id = {batch_id.id}" 
                
            if status_attendance != False:
                where_string +=f" AND a.state = {status_attendance}"     
                                           
            self.env.cr.execute(f"""CREATE or REPLACE VIEW oe_school_dynamic_report as (
             SELECT            
                   a.id as id,
                   a.date_attendance as date,
                   a.student_id as partner_id,
                   a.course_id as course_id,
                   a.subject_id as subject_id,
                   a.batch_id as batch_id,
                   a.state as  status_attendance,
                   a.is_late as is_late
            FROM oe_school_attendance a """ +where_string+ """
          
             
        
            )""" )
        

            return {
                'name': _('Attendance Detail Analysis checkpoint'),
                'view_mode': 'tree',
                'res_model': 'oe.school.dynamic.report',
                'view_id': False,
                'type': 'ir.actions.act_window',
        
                
            }
        
    