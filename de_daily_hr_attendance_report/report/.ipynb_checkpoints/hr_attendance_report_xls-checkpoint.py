# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError
from datetime import datetime
from datetime import date, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
import datetime
import pytz
import calendar


class EmployeeAttendanceXlS(models.AbstractModel):
    _name = 'report.de_daily_hr_attendance_report.hr_attendance_report_xlsx'
    _description = 'Employee Attendance Xlsx report'
    _inherit = 'report.report_xlsx.abstract'
    
  
    def generate_xlsx_report(self, workbook, data, lines):
        data = self.env['hr.attendance.report.wizard'].browse(self.env.context.get('active_ids'))
        format1 = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': False})
        sheet = workbook.add_worksheet('Employee Attendance Report')
        bold = workbook.add_format({'bold': True, 'align': 'center', 'border': True})
        
        sheet.write('D2:D2', 'Employee Attendance', bold)
        sheet.write('C3:C3', 'date from: '+ data.on_date .strftime('%d-%b-%Y'), bold)
        sheet.write('E3:E3', 'date to: '+ data.date_to .strftime('%d-%b-%Y'), bold)

        
        
        
        sheet.set_column('A:B', 20, )
        sheet.set_column('C:C', 30, )
        sheet.set_column('D:D', 30, )
        sheet.set_column('E:F', 30, )
        sheet.set_column('G:H', 20, )
        sheet.set_column('I:J', 20, )
        
        
        sheet.write(5, 0, 'Sr No', bold)
        sheet.write(5, 1, 'Empolyee', bold)
        sheet.write(5, 2, 'Present/Absent', bold)
        sheet.write(5, 3, 'Check in', bold)
        sheet.write(5, 4, 'Check out', bold)
        sheet.write(5, 5, 'Present', bold)
        sheet.write(5, 6, 'Absent', bold)
        
        
        
        sr_no = 0
        count = 0
        count_att = 0
        
    
        
#         date_list = []
#         if data.printed_by == 'daily':
#             date_list.append(data.on_date)
            
#         elif data.printed_by == 'weekly':
#             date_list.append(data.on_date)
#             for day in range(7):
#                 date_list.append(data.on_date + datetime.timedelta(days=day))
                
#         if data.printed_by == 'monthly':
#             date_list.append(data.on_date)
#             for day in range(31):
#                 date_list.append(data.on_date + datetime.timedelta(days=day))
            
            
            
            
            
#             on_date = data.on_date
#             weekday = on_date.weekday()
#             start_delta = datetime.timedelta(days=weekday)
#             start_of_week = on_date + start_delta
#             for day in range(31):
#                 date_list.append(start_of_week - datetime.timedelta(days=day))

        sr_no += 1
        row = 7
        row_out = 7
        if data.all_employees:
            employees = self.env['hr.employee'].search([])
            
        if data.employee:
            
            employees = self.env['hr.employee'].search([('id','=', data.employee.id)])
            
            
        delta_days = (data.date_to - data.on_date).days + 1
        
        
        for l in employees:
            
            start_date = data.on_date 
            delta_days = (data.date_to - data.on_date).days + 1
            for dayline in range(delta_days):

                hr_attendance = self.env['hr.attendance'].search([('employee_id', '=', l.id),('attendance_date','=',start_date)], order="check_in asc")
                count = 0
                for count_line in hr_attendance:
                    count += 1
                
                count_att = 0
                check_in = False
                check_out = False
                for line in hr_attendance:
                    sheet.write(row_out, 1, l.name, format1) 
                    sheet.write(row, 0, sr_no, format1)

                    if line.check_in and line.check_out:
                        sheet.write(row, 2, 'P', format1)
                        sheet.write(row, 5, '1', format1)
                        sheet.write(row, 6, '0', format1)
                    else:
                        sheet.write(row, 2, 'A', format1)
                        sheet.write(row, 5, '0', format1)
                        sheet.write(row, 6, '1', format1)


                    count_att += 1
                    if count_att == 1:
                        check_in = (line.check_in)
                    if count_att == count:
                        check_out = (line.check_out)
                    
                    check_in_time = check_in
                    check_out_time = check_out    
                    if check_in:
                        check_in_time = check_in + relativedelta(hours=+5)
                        sheet.write(row, 3, check_in_time.strftime('%m/%d/%Y %H:%M:%S'), format1)
                    if check_out: 
                        check_out_time = check_out + relativedelta(hours=+5)
                        sheet.write(row, 4,check_out_time.strftime('%m/%d/%Y %H:%M:%S'), format1)

                    
                    
#                 if hr_attendance.check_in:
#                     sheet.write(row, 3, hr_attendance.check_in.strftime('%d/%m/%Y %H:%M:%S') + relativedelta(hours =+ 5), format1)
#                 if hr_attendance.check_out:
#                     sheet.write(row, 4, hr_attendance.check_out.strftime('%d-%m-%Y %H:%M:%S'), format1)
                    
                    
                row = row+1
                start_date = (start_date + timedelta(1))    
#                 else:
#                     att_dates = self.env['hr.attendance'].search([('attendance_date','>=', data.on_date),('attendance_date','<=', data.date_to)])
#                     for date in att_dates:
#                         sheet.write(row, 2, 'A', format1)
#                         sheet.write(row, 5, '0', format1)
#                         sheet.write(row, 6, '1', format1)
#                         sheet.write(row, 3, '', format1)
#                         sheet.write(row, 4, '', format1)

#                         row = row+1
                sr_no += 1

                row_out = row