# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrAttendanceReportWizard(models.TransientModel):
    _name = 'hr.attendance.report.wizard'
    _description = 'Daily Attendance Report'

    on_date = fields.Date(string='Date from', required=True)
    date_to = fields.Date(string='Date to', required=True)
    
#     printed_by = fields.Selection(selection=[
#             ('daily', 'Daily'),
#             ('weekly', 'Weekly'),
#             ('monthly', 'Monthly'),
#         ], string='Print By', default='daily')
    all_employees = fields.Boolean(string="All Employees")
    employee = fields.Many2one('hr.employee', string="Employee")
    
    
   
    
    
    
    def check_report(self):
        data = {}
        data['form'] = self.read(['on_date', 'date_to' 'all_employees', 'employee'])[0]
        return self.print_hr_attendance_report_xls(data)
        

    def print_hr_attendance_report_xls(self):
        data = {}
        data['form'] = self.read(['on_date','date_to', 'employee', 'all_employees'])[0]
        return self.env.ref('de_daily_hr_attendance_report.hr_attendance_report_xlsx').report_action(self, data=data, config=False)
    
    

#     def print_hr_attendance_report_xls(self):

#         data = {
#             'on_date': self.on_date,
# #             'stop_at': self.stop_at,
# #             'shop_ids': self.shop_ids.ids,
#         }
#         return self.env.ref('de_daily_hr_attendance_report.hr_attendance_report_xlsx').report_action(self, data=data)
