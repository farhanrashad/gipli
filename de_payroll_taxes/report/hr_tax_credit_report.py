import json
from odoo import models
from odoo.exceptions import UserError


class PayrollTaxCreditReport(models.AbstractModel):
    _name = 'report.de_payroll_taxes.hr_tax_credit_report_xlx'
    _description = 'Tax Credit report'
    _inherit = 'report.report_xlsx.abstract'
    
    
    
    def generate_xlsx_report(self, workbook, data, lines):
        format1 = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': False})
        sheet = workbook.add_worksheet('Tax Credit Report')
        bold = workbook. add_format({'bold': True, 'align': 'center','border': True})
        
        sheet.set_column('A:B', 20,)
        sheet.set_column('C:D', 20,)
        sheet.set_column('E:F', 20,)
        sheet.set_column('G:H', 20,)
        sheet.set_column('I:J', 20,)
        sheet.set_column('K:L', 20,)
        sheet.write(1,0, 'company',bold)
        sheet.write(1,1, 'Employee Number',bold)
        sheet.write(1,2, 'Employee' ,bold)
        sheet.write(1,3, 'Reason' ,bold)
        sheet.write(1,4, 'Tax Credit Type' ,bold)
        sheet.write(1,5, 'Post',bold)
        sheet.write(1,6, 'Current Amount',bold)
        sheet.write(1,7, 'Period Name',bold)
        sheet.write(1,8, 'Dist Month',bold)
        row = 3
        for line in lines: 
            sheet.write(row, 0, line.company_id.name, format1)
            sheet.write(row, 1, line.employee_id.emp_number, format1)
            sheet.write(row, 2, line.employee_id.name, format1)
            sheet.write(row, 3, line.remarks, format1)
            sheet.write(row, 4, line.credit_type_id.name, format1)  
            sheet.write(row, 5, line.post, format1)
            sheet.write(row, 6, line.tax_amount, format1) 
            sheet.write(row, 7, str(line.date.strftime('%B-%y')), format1)
            sheet.write(row, 8, line.dist_month, format1)
            row += 1           