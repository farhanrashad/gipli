# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import xlsxwriter
import io
import base64
import itertools
from odoo.exceptions import UserError, AccessError
import psycopg2


class StudentAttendanceReport(models.TransientModel):
    """ Wizard for Attendance XLSX Report """
    _name = 'oe.report.student.attendance.xlsx.wizard'
    _description = 'Student Attendance XLSX Report Wizard'

    date_from = fields.Date(string="From date",required=True)
    date_to = fields.Date(string="To Date", required=True)

    course_id = fields.Many2one('oe.school.course',string="Course", required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    def generate_excel_report(self):

        
        self.ensure_one()
        file_path = 'attendance_detail_report_' + str(fields.Date.today()) + '.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/' + file_path)

        heading = workbook.add_format({'font_size': '12', 'align': 'center', 'bold': True,'border':True})
        title = workbook.add_format({'font_size': '10', 'align': 'center', 'bold': True, 'border':True, 'bg_color': '#ccffff'})
                
        text = workbook.add_format({'font_size': '10', 'align': 'left', 'border':True,})
        number = workbook.add_format({'font_size': '10', 'align': 'right', 'num_format':'#,##0.00', 'border':True})
        
        text_total = workbook.add_format({'font_size': '14', 'align': 'left', 'border':True, 'bold':True, 'bg_color': '#ccffff'})
        number_total = workbook.add_format({'font_size': '14', 'bold':True, 'align': 'right', 'num_format':'#,##0.00', 'border':True, 'bg_color': '#ccffff'})

        sheet = workbook.add_worksheet('Attendance Details')

        sheet.merge_range(0, 0, 0, 6, 'Loan Details Report', heading)
        
        sheet.write(1, 0, 'Date', heading)
        sheet.merge_range(1, 1, 1, 2, (str(self.date_from) + ' - ' + str(self.date_to)), text)

        sheet.write(1, 3, 'Loan Type(s)', heading)
        sheet.merge_range(1, 4, 1, 6, self.course_id.name, text)

        query = """
            SELECT s.name as student, t.date_attendance, t.attendance_type
                from oe_student_attendance t
                join res_partner s on t.student_id = s.id
                WHERE t.date_attendance >= %(date_from)s and t.date_attendance <= %(date_to)s
                and t.company_id = %(company_id)s
        """

        args = {
            'company_id': self.company_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'course_id': self.course_id.id
        }
        self.env.cr.execute(query, args)
        rs_attendance = self._cr.dictfetchall()

        raise UserError(len(rs_attendance))
        sheet.write(2, 0, 'Student', title)
        sheet.write(2, 1, 'Date', title)
        sheet.write(2, 2, 'Status', title)

        row = 3
        
        if len(rs_attendance):
            for attend in rs_attendance:
                sheet.set_column(row, 0, 20)
                sheet.set_column(row, 1, 20)
                sheet.set_column(row, 2, 30)

                sheet.write(row, 0, attend['student'],text)
                sheet.write(row, 1, attend['date_attendance'],text)
                sheet.write(row, 2, attend['attendance_type'],text)

                row += 1
            
        else:
            sheet.merge_range(row , 3, row , 5,"No Data Was Found For This student In Selected Date", formate_1)
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


