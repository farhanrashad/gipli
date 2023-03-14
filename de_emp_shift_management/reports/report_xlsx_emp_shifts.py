from odoo import models, fields, api,_
from datetime import datetime
from odoo.exceptions import ValidationError, UserError

class ReportEmpShiftXlsx(models.AbstractModel):
    _name = 'report.de_emp_shift_management.employee_shift_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        format1 = workbook.add_format(
            {'font_size': 12, 'align': 'vcenter', 'bold': True, 'bg_color': '#d3dde3', 'color': 'black',
             'bottom': True, })
        format2 = workbook.add_format(
            {'font_size': 12, 'align': 'vcenter', 'bold': True, 'bg_color': '#edf4f7', 'color': 'black',
             'num_format': '#,##0.00'})
        format3 = workbook.add_format({'font_size': 11, 'align': 'vcenter', 'bold': False, 'num_format': '#,##0.00'})
        format3_colored = workbook.add_format(
            {'font_size': 11, 'align': 'vcenter', 'bg_color': '#f7fcff', 'bold': False, 'num_format': '#,##0.00'})
        format4 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True})
        format5 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': False})

        sheet = workbook.add_worksheet("Customer Export")
        customers = self.env['res.partner'].search([])
        sheet.merge_range(0,3, 0, 6,"Employee Shift Allocation",format4) 
        sheet.write(3, 0, 'Name', format1)
        sheet.write(3, 1, 'Employee', format1)
        sheet.write(3, 2, 'Date from', format1)
        sheet.write(3, 3, 'Date to', format1)
        sheet.write(3, 4, 'Shift', format1)
        sheet.write(3, 5, 'State', format1)
        
        wiz_obj=self.env['wizard.report.emp.shift'].browse(data['ids'])
        emp_recs = self.env['employee.shift.alloc'].search([('date_from','>=',wiz_obj.date_from),('date_to','<=',wiz_obj.date_to)])
        
        row=4
        for rec in emp_recs:
            sheet.write(row, 0,rec.name , format5)
            sheet.write(row, 1,rec.employee_id.name , format5) 
            sheet.write(row, 2,rec.date_from, format5)
            sheet.write(row, 3,rec.date_to, format5)
            sheet.write(row, 4,rec.shift_id.name, format5)
            sheet.write(row, 5,rec.state, format5)
            row+=1
        
        
        
        