from odoo import models, fields, api,_


class deEmpWeekoff(models.Model):
    _name = 'emp.weekoff'
    
    name = fields.Char(string= 'Name' , required= True)
    day_no = fields.Integer(string = 'Day no')
    shift_allocation_id = fields.Many2one("employee.shift.alloc", string = "Shift Allocation id")
 
class deShiftType(models.Model):
    _name = 'shift.type'
    
    name = fields.Char(string= 'Name' , required= True)
    work_hours = fields.Float(string = 'Work Hours')
    
    
class deEmpShifts(models.Model):
    _name = 'emp.shift'
    
    name = fields.Char(string= 'Name' , required= True)
    shift_id = fields.Many2one('shift.type',string = 'Shift Type')
    time_from = fields.Float(string = 'Time From') 
    time_to = fields.Float(string = 'Time to')
    user_id = fields.Many2one('res.users' , string= 'Responsible',default=lambda self: self.env.user,)   
    resource_calendar_id = fields.Many2one('resource.calendar', string = 'Working Hours')
    over_time_threshold =fields.Float(string = 'Over Time Threshold') 
    late_threshold =fields.Float(string = 'Late Threshold')
    company_id = fields.Many2one('res.company' ,string = 'Company')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Favorite'),
    ], default='0', string="Favorite")
    related_weekoff_count=fields.Integer('Number of related Weekoff', compute='_compute_related_weekoff_count')
    # related_weekdays_count=fields.Integer('Number of related WeekDays', compute='_compute_related_weekday_count')
    #
    def _compute_related_weekoff_count(self):
        for rec in self:
            # rec.related_weekoff_count = len(self.env['shift.management'].search([('employee_id','=', employee.id)]))
            rec.related_weekoff_count =5
    
    
    def action_related_weekoff(self):
        self.ensure_one()
        return {
            'name': _("Related Weekoff"),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'emp.weekoff',
             'domain': []
        }
    
    # def _compute_related_weekday_count(self):
    #     for rec in self:
    #         # rec.related_weekoff_count = len(self.env['shift.management'].search([('employee_id','=', employee.id)]))
    #         rec.related_weekdays_count =5 
    #
    
class deShiftDays(models.Model):
    _name = 'shift.days'
    _rec_name ="employee_id"
    
    
   
    shift_id = fields.Many2one('emp.shift',string = 'Shift')
    employee_id = fields.Many2one("hr.employee", string = "Employee")     
    date_of_week = fields.Date(string="Date of week")
    department_id =fields.Many2one("hr.department", string = "Department")
    user_id = fields.Many2one('res.users' , string= 'Responsible',default=lambda self: self.env.user)   
    shift_allocation_id = fields.Many2one("employee.shift.alloc", string = "Shift Allocation id")
      
      
class deShiftOffDays(models.Model):
    _name = 'shift.offdays'
    _rec_name ="employee_id"
    
    
   
    shift_id = fields.Many2one('emp.shift',string = 'Shift')
    employee_id = fields.Many2one("hr.employee", string = "Employee")     
    date_of_week = fields.Date(string="Date of week")
    day_of_week =fields.Many2one("emp.weekoff", string = "Day of week")
    user_id = fields.Many2one('res.users' , string= 'Responsible',default=lambda self: self.env.user)   
    shift_allocation_id = fields.Many2one("employee.shift.alloc", string = "Shift Allocation id")
      
            
      
      