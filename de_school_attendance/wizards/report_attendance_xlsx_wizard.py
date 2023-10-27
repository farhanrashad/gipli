# -*- coding: utf-8 -*-


import io
import json
import base64

from datetime import datetime, date
from dateutil.rrule import rrule, DAILY

from odoo import fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
    
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

        
        
        border = workbook.add_format({'border': 1})
        green = workbook.add_format({'bg_color': '#28A828', 'border': 1})
        red = workbook.add_format({'bg_color': '#ff3333', 'border': 1})
        rose = workbook.add_format({'bg_color': '#DA70D6', 'border': 1})
        
        sheet = workbook.add_worksheet('Attendance Details')

        sheet.merge_range(0, 0, 0, 6, 'Attendance Details Report', heading)
        
        sheet.write(1, 0, 'Date', heading)
        sheet.merge_range(1, 1, 1, 2, (str(self.date_from) + ' - ' + str(self.date_to)), title)

        sheet.write(1, 3, 'Course', heading)
        sheet.merge_range(1, 4, 1, 6, self.course_id.name, title)

        start_date = self.date_from #datetime.strptime(self.date_from, '%Y-%m-%d').date()
        end_date = self.date_to #datetime.strptime(self.date_to, '%Y-%m-%d').date()

        sheet.set_column(1, 1, 15)
        sheet.set_column(2, 2, 15)
        
        query = """
            select p.name, a.date_attendance as date,
                a.attendance_status,
                p.roll_no, p.admission_no, guardian.name as guardian_name
            from oe_student_attendance a 
            LEFT JOIN res_partner p on a.student_id = p.id
            LEFT JOIN res_partner guardian on p.guardian_id = guardian.id
            LEFT join oe_school_course c on p.course_id = c.id
            LEFT join oe_school_course_batch b on b.course_id = b.id
            """
        self.env.cr.execute(query)
        docs = self.env.cr.dictfetchall()

        date_range = rrule(DAILY, dtstart=start_date, until=end_date)

        row = 3
        col = 6
        for date_data in date_range:
            col += 1
            sheet.set_column(row, col, 10)
            sheet.write(row, col, date_data.strftime('%Y-%m-%d'), border)
        row = 4
        col = 6
        for date_data in date_range:
            col += 1
            sheet.set_column(row, col, 10)
            sheet.write(row, col, date_data.strftime('%a'), border)

        # Student Date
        student_names = []
        attendance_list = []
        for doc in docs:
            if doc['name'] not in student_names:
                date_sum_list = []
                student_names.append(doc['name'])
                for date_data in date_range:
                    date_out = date_data.strftime('%Y-%m-%d')
                    record_list = list(
                        filter(
                            lambda x: x['name'] == doc['name'] and x[
                                'date'].strftime(
                                '%Y-%m-%d') == date_out, docs))
                    if record_list:
                        date_sum_list.append(record_list[0])
                    else:
                        date_sum_list.append({
                            'name': '',
                            'date': '',
                            'attendance_status': 0
                        })
                attendance_list.append({
                    'name': doc['name'],
                    'status': doc['attendance_status'],
                    'items': date_sum_list
                })
        
        row = 4
        i = 0
        for rec in attendance_list:
            row += 1
            col = 0
            i += 1
            sheet.write(row, col, i, border)
            col += 1
            sheet.write(row, col, rec['name'], border)
            col += 1
            sheet.write(row, col, rec['name'], border)
            col += 1
            sheet.write(row, col, rec['name'], border)
            col += 1
            sheet.write(row, col, rec['name'], border)
            col += 1
            sheet.write(row, col, rec['name'], border)
            col += 1
            sheet.write(row, col, rec['name'], border)
            for item in rec['items']:
                col += 1
                if item['attendance_status'] == 'present':
                    sheet.write(row, col, 'P', green)
                elif item['attendance_status'] == 'absent':
                    sheet.write(row, col, 'A', red)
                #        work.hours_per_day:
                #    sheet.write(row, col, item['sum'], rose)
                #else:
                #    sheet.write(row, col, item['sum'], red)


        workbook.close()
        ex_report = base64.b64encode(open('/tmp/' + file_path, 'rb+').read())

        excel_report_id = self.env['oe.attendance.save.xlsx'].create({"document_frame": file_path,
                                                                        "file_name": ex_report})

        return {
            'res_id': excel_report_id.id,
            'name': 'Files to Download',
            'view_type': 'form',
            "view_mode": 'form',
            'view_id': False,
            'res_model': 'oe.attendance.save.xlsx',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


