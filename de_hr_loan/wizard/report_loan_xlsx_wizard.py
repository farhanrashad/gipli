# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import xlsxwriter
import io
import base64
import itertools
from odoo.exceptions import ValidationError
import psycopg2


class HrAttendanceReport(models.TransientModel):
    """ Wizard for Employee Attendance Report """
    _name = 'employee.attendance.report'
    _description = 'Employee Attendance Report Wizard'

    start_date = fields.Date(string="Start date",required=True)
    end_date = fields.Date(string="End Date",required=True)

    employee_ids = fields.Many2many('hr.employee',string="Select employee",required=True)


    def generate_pdf_report(self):
        if self.start_date > self.end_date:
            raise ValidationError(_("Invalid Date !! End date should be greater than the start date"))
        else:
            data_dict = {'id': self.id,'start_date': self.start_date, 'end_date': self.end_date,'employee_ids':self.employee_ids}
            return self.env.ref('bi_employee_timesheet_report.timesheet_report_id').report_action(self,
                                                                                                 data=data_dict)

    def generate_excel_report(self):

        if self.start_date > self.end_date:
            raise ValidationError(_("Invalid Date !! End date should be greater than the start date"))
        else:
            self.ensure_one()
            file_path = 'loan_detail_report_' + str(fields.Date.today()) + '.xlsx'
            workbook = xlsxwriter.Workbook('/tmp/' + file_path)

            title_format = workbook.add_format(
                {'border': 1, 'bold': True, 'valign': 'vcenter', 'align': 'center', 'font_size': 11, 'bg_color': '#D8D8D8'})

            formate_1 = workbook.add_format({'bold': True, 'align': 'center', 'font_size': 11,'font_color':'red'})

            heading = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': True,'border':True})
            title = workbook.add_format({'font_size': '10', 'align': 'center', 'bold': True, 'border':True, 'bg_color': '#ccffff'})
                
            text = workbook.add_format({'font_size': '10', 'align': 'left', 'border':True,})
            number = workbook.add_format({'font_size': '10', 'align': 'right', 'num_format':'#,##0.00', 'border':True})
        
            text_total = workbook.add_format({'font_size': '14', 'align': 'left', 'border':True, 'bold':True, 'bg_color': '#ccffff'})
            number_total = workbook.add_format({'font_size': '14', 'bold':True, 'align': 'right', 'num_format':'#,##0.00', 'border':True, 'bg_color': '#ccffff'})

        

            record = self.env['account.analytic.line'].search(
                [('employee_id', 'in', self.employee_ids.ids), ('date', '>=', self.start_date),
                 ('date', '<=', self.end_date)])

            sheet = workbook.add_worksheet('Loan Detail')

            query = """
                SELECT
                    ln.name, to_char(ln.date,'MM-DD-YYYY') as date, 
                    e.name as employee_name, tp.name -> 'en_US' as loan_type,
                    ln.amount as loan_amount, ln.amount_paid, ln.amount_disbursed, ln.amount_balance, ln.state,
                    to_char(l.date,'MM-DD-YYYY') as due_date, l.amount as due_amount, l.state as due_status
                FROM hr_loan ln
                JOIN hr_loan_line l on l.loan_id = ln.id
                JOIN hr_employee e on ln.employee_id = e.id
                JOIN hr_loan_type tp on ln.loan_type_id = tp.id
        
            """
            args = {
                #'company_id': company_id,
                'date_from': self.start_date,
                'date_to': self.end_date,
            }
            self.env.cr.execute(query, args)
            rs_loans = self._cr.dictfetchall()

            sheet.write(1, 0, 'Reference', title)
            sheet.write(1, 1, 'Date', title)
            sheet.write(1, 2, 'Employee', title)
            sheet.write(1, 3, 'Loan Type', title)
            sheet.write(1, 4, 'Due Date', title)
            sheet.write(1, 5, 'Due Amount', title)
            sheet.write(1, 6, 'Due Status', title)

            row = 2
            
            if len(rs_loans):
                for loan in rs_loans:
                    sheet.set_column(row, 0, 20)
                    sheet.set_column(row, 1, 20)
                    sheet.set_column(row, 2, 30)
                    sheet.set_column(row, 3, 20)
                    sheet.set_column(row, 4, 10)
                    sheet.set_column(row, 5, 10)
                    sheet.set_column(row, 6, 10)

                    sheet.write(row, 0, loan['name'],text)
                    sheet.write(row, 1, loan['date'],text)
                    sheet.write(row, 2, loan['employee_name'],text)
                    sheet.write(row, 3, loan['loan_type'],text)
                    sheet.write(row, 4, loan['due_date'],text)
                    sheet.write(row, 5, loan['due_amount'],number)
                    sheet.write(row, 6, loan['due_status'],text)

                    row += 1

            # Loan Summary
            sheet = workbook.add_worksheet('Loan Summary')

            query = """
                SELECT
                    ln.name, to_char(ln.date,'MM-DD-YYYY') as date, 
                    e.name as employee_name, tp.name -> 'en_US' as loan_type,
                    ln.amount as loan_amount, ln.amount_paid, ln.amount_disbursed, ln.amount_balance, ln.state
                FROM hr_loan ln
                JOIN hr_employee e on ln.employee_id = e.id
                JOIN hr_loan_type tp on ln.loan_type_id = tp.id
        
            """
            args = {
                #'company_id': company_id,
                'date_from': self.start_date,
                'date_to': self.end_date,
            }
            self.env.cr.execute(query, args)
            rs_loans = self._cr.dictfetchall()

            sheet.write(1, 0, 'Reference', title)
            sheet.write(1, 1, 'Date', title)
            sheet.write(1, 2, 'Employee', title)
            sheet.write(1, 3, 'Loan Type', title)
            sheet.write(1, 4, 'Loan Amount', title)
            sheet.write(1, 5, 'Paid Amount', title)
            sheet.write(1, 6, 'Disbursed', title)
            sheet.write(1, 7, 'Residual', title)
            sheet.write(1, 8, 'Status', title)
            
            row = 2
            
            if len(rs_loans):
                for loan in rs_loans:
                    sheet.set_column(row, 0, 20)
                    sheet.set_column(row, 1, 20)
                    sheet.set_column(row, 2, 30)
                    sheet.set_column(row, 3, 20)
                    sheet.set_column(row, 4, 10)
                    sheet.set_column(row, 5, 10)
                    sheet.set_column(row, 6, 10)
                    sheet.set_column(row, 7, 10)
                    sheet.set_column(row, 8, 10)

                    sheet.write(row, 0, loan['name'],text)
                    sheet.write(row, 1, loan['date'],text)
                    sheet.write(row, 2, loan['employee_name'],text)
                    sheet.write(row, 3, loan['loan_type'],text)
                    sheet.write(row, 4, loan['loan_amount'],number)
                    sheet.write(row, 5, loan['amount_paid'],number)
                    sheet.write(row, 6, loan['amount_disbursed'],number)
                    sheet.write(row, 7, loan['amount_balance'],number)
                    sheet.write(row, 8, loan['state'],text)

                    row += 1
                    
            
            else:
                sheet.merge_range(row , 3, row , 5,"No Data Was Found For This Employee In Selected Date", formate_1)
                row += 4



            workbook.close()
            ex_report = base64.b64encode(open('/tmp/' + file_path, 'rb+').read())

            excel_report_id = self.env['hr.loan.save.xlsx.wizard'].create({"document_frame": file_path,
                                                                        "file_name": ex_report})

            return {
                'res_id': excel_report_id.id,
                'name': 'Files to Download',
                'view_type': 'form',
                "view_mode": 'form',
                'view_id': False,
                'res_model': 'hr.loan.save.xlsx.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }


