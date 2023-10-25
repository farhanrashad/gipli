from odoo import models, fields, api,_
from datetime import datetime , date, timedelta
from odoo.exceptions import ValidationError, UserError
import calendar


class DeSchoolAttendance(models.Model):
    _name = "oe.school.attendance"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    
    
    name = fields.Char(
        string="Name",
        required=True, copy=False, readonly=True,
        default=lambda self: _('New'))
     
    school_year_id= fields.Many2one("oe.school.year", string="Year", required=True )
    date_attendance= fields.Datetime(string="Attendance Date", required=True )
    student_id= fields.Many2one("res.partner", string="Student", required=True )
    period_id= fields.Many2one("resource.calendar.attendance", string="Period" )
    course_id= fields.Many2one("oe.school.course", string="Course" )
    subject_id= fields.Many2one("oe.school.course.subject", string="Subject" )
    batch_id= fields.Many2one("oe.school.course.batch", string="Batch" )
    by_period= fields.Boolean('by period',compute="check_attendance_mode" , store= True)
    company_id = fields.Many2one("res.company", string="company", default = lambda self:self.env.company)
                                 
    state =  fields.Selection(
        selection=[
            ('draft', "Draft"),
            ('present', "Present"),
            ('absent', "Absent"),
            
       ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=True,
        default='draft')
    
    is_late= fields.Boolean(string="Late", default=False)
    
    # resource_calendar_id =fields.Many2one( )
    @api.depends('company_id.attendance_mode')
    def check_attendance_mode(self):
        for res in self:
            if res.env.company.attendance_mode == 'period':
                res.by_period = True
            else:
                res.by_period = False
              
    def button_present(self):
        self.state= 'present'        
    
    
    def button_absent(self):
        self.state= 'absent'  
        
             
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('oe.school.attendance') or _('New')
        res = super(DeSchoolAttendance, self).create(vals_list)
        return res
    
        
class deSchoolStudent(models.Model):
    _inherit= "res.partner"
    
    is_student = fields.Boolean(string= "Is Student")        
    
    