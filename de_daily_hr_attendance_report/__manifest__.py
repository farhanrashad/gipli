# -*- coding: utf-8 -*-
{
    'name': 'Daily Attendance Report xlsx',
    'version': '14.0',
    "category": "Attendance",
    'depends': ['hr_attendance', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_attendance_report_xls.xml',
        'views/attendance_form.xml',
        'wizard/hr_attendance_report_wizard.xml',
    ],
    'installable': True,
    'auto_install': False,
}