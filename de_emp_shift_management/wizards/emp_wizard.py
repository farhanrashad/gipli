from odoo import models, fields, api,_
from datetime import datetime , date, timedelta
from odoo.exceptions import ValidationError, UserError
import calendar
class WizShifAlloc(models.TransientModel):
    _name = 'wizard.shift.alloc'
    
    
    shift_id = fields.Many2one("emp.shift", string = "Shift")
    shift_type_id = fields.Many2one('shift.type',string = 'Shift Type')
    date_from = fields.Date(string='Date From', required=True, default=datetime.today())
    date_to = fields.Date(string='Date To', required=True, default=datetime.today())
    employee_ids = fields.Many2many('hr.employee', string= "Employee")
    description = fields.Text(string ="Text")
    
    def get_all_dates(self,date_from,date_to):
       
        date_list=[]
        delta = date_to - date_from   # returns timedelta

        for i in range(delta.days + 1):
            day = date_from + timedelta(days=i)
            date_list.append(day)
        return date_list    
    
    def getStatus(self,date_list):
        workday_list=[]
        offday_list =[]
    
        for dt in date_list:
            if dt.strftime("%A").upper() != "SATURDAY":
                workday_list.append((0,0 ,{
                                   'date_of_week':dt,
                                   'shift_id':self.shift_id.id,
                                   
                                    } ))
            else:
                day_name= dt.strftime("%A")
                day_obj =self.env['emp.weekoff'].search([('name','=',day_name.capitalize()) or ('name','=',day_name.upper()) or ('name','=',day_name.lower())])
                
                offday_list.append((0,0 ,{
                                   'date_of_week':dt,
                                   'shift_id':self.shift_id.id,
                                    'day_of_week':day_obj.id
                                   
                                    } ))      
               
    
        return workday_list,offday_list 
    
    def create_shifts(self):
        try:
            workday_list=[]
            offday_list =[]
            all_dates = self.get_all_dates(self.date_from, self.date_to)
            workday_list,offday_list= self.getStatus(all_dates) 
            # for dt in all_dates:
            #         if dt.strftime("%A").upper() != "SATURDAY":
            #             workday_list.append((0,0 ,{
            #                                'date_of_week':dt,
            #                                'shift_id':self.shift_id.id,
            #
            #                                 } ))
            #         else:
            #             day_name= dt.strftime("%A")
            #             day_obj =self.env['emp.weekoff'].search([('name','=',day_name.capitalize()) or ('name','=',day_name.upper()) or ('name','=',day_name.lower())])
            #
            #             offday_list.append((0,0 ,{
            #                                'date_of_week':dt,
            #                                'shift_id':self.shift_id.id,
            #                                 'day_of_week':day_obj.id
            #
            #                                 } ))      
            #

            for emp in self.employee_ids:
                emp_workday_list=[]
                emp_offday_list=[]
                emp_date_range=[]
               
                for item in workday_list:
                    emp_shiftObj= self.env['shift.days'].search([('employee_id','=',emp.id),('date_of_week','=',item[2]['date_of_week'])])
                    if not emp_shiftObj: 
                        item[2].update( {'employee_id':emp.id})
                        emp_workday_list.append(item)
                        emp_date_range.append(item[2]['date_of_week'])  
                    # else:
                    #     workday_list.pop(workday_list.index(item)) 
                
                for l in offday_list:
                    emp_OffshiftObj= self.env['shift.offdays'].search([('employee_id','=',emp.id),('date_of_week','=',l[2]['date_of_week'])])
                    if not emp_OffshiftObj: 
                        l[2].update( {'employee_id':emp.id})
                        emp_offday_list.append(l)
                        emp_date_range.append(l[2]['date_of_week'])
                        
                         
                emp_date_range.sort()
                
                rec = self.env['employee.shift.alloc'].create({
                    'shift_id': self.shift_id.id,
                    'shift_type_id': self.shift_type_id.id,
                    'date_from': emp_date_range[0],
                    'date_to': emp_date_range[-1],
                    'state': 'done',
                    'employee_id':emp.id, 
                    'shift_days_line' :emp_workday_list,
                    'shift_offdays_line' :emp_offday_list,
                })
                  
                print(rec)
        
        except Exception as e:
            print(e.args)
        
        