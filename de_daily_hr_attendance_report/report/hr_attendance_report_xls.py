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
        
        sheet.write('C2:C2', 'Employee Attendance', bold)
        sheet.write('C3:C3', 'daily: '+ data.on_date .strftime('%d-%b-%Y'), bold)
        
        
        
        sheet.set_column('A:B', 20, )
        sheet.set_column('C:C', 30, )
        sheet.set_column('D:D', 20, )
        sheet.set_column('E:F', 20, )
        sheet.set_column('G:H', 20, )
        sheet.set_column('I:J', 20, )
        
        
        sheet.write(5, 0, 'Sr No', bold)
        sheet.write(5, 1, 'Empolyee', bold)
        sheet.write(5, 2, data.on_date .strftime('%d-%b-%Y'), bold)
        sheet.write(5, 3, 'Check in', bold)
        sheet.write(5, 4, 'Check out', bold)
        sheet.write(5, 5, 'Present', bold)
        sheet.write(5, 6, 'Absent', bold)
        
        
        row = 7
        sr_no = 0
        
    
        
        date_list = []
        if data.printed_by == 'daily':
            date_list.append(data.on_date)
            
        elif data.printed_by == 'weekly':
            date_list.append(data.on_date)
            for day in range(7):
                date_list.append(data.on_date + datetime.timedelta(days=day))
                
        if data.printed_by == 'monthly':
            on_date = data.on_date
            weekday = on_date.weekday()
            start_delta = datetime.timedelta(days=weekday)
            start_of_week = on_date + start_delta
            for day in range(31):
                date_list.append(start_of_week - datetime.timedelta(days=day))

            sr_no += 1
        if data.all_employees:
            employees = self.env['hr.employee'].search([]).ids
        if data.employee:
            employees = self.env['hr.employee'].search([('id','=', data.employee.id)]).ids
            
        hr_attendance = self.env['hr.attendance'].search([('attendance_date','in', date_list),('employee_id', 'in', employees)])
        
       
        for line in hr_attendance:
            sheet.write(row, 0, sr_no, format1)
            sheet.write(row, 1, line.employee_id.name, format1)
            if line.check_in and line.check_out:
                sheet.write(row, 2, 'P', format1)
                sheet.write(row, 5, '1', format1)
                sheet.write(row, 6, '0', format1)
            else:
                sheet.write(row, 2, 'A', format1)
                sheet.write(row, 5, '0', format1)
                sheet.write(row, 6, '1', format1)
            sheet.write(row, 3, line.check_in.strftime('%d/%m/%Y %H:%M:%S'), format1)
            if line.check_out:
                sheet.write(row, 4, line.check_out.strftime('%d-%m-%Y %H:%M:%S'), format1)
                
            
            row = row+1
            sr_no += 1
            
            

#                 sheet.write(row, 4, total_hours, format1)
#             +
            
        
        