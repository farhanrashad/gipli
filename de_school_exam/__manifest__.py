# -*- coding: utf-8 -*-
{
    'name': "Openrol - Exams",

    'summary': """
    School Examiniation
        """,

    'description': """
        Examaniation
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'School/Industries',
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['de_school'],

    # always loaded
    'data': [
        'security/exam_security.xml',
        'security/ir.model.access.csv',
        'data/exam_data.xml',
        'data/ir_sequence.xml',
        'views/exam_menu.xml',
        'views/exam_type_views.xml',
        'views/exam_grade_views.xml',
        'views/marksheet_group_views.xml',
        'views/course_views.xml',
        'views/exam_session_views.xml',
        'views/exam_views.xml',
        'views/mark_sheet_views.xml',
        'views/exam_result_views.xml',
        'views/exam_attendees_views.xml',
        'reports/report_exam_sheet.xml',
        'reports/report_result_sheet.xml',
        'reports/report_exam_tickets.xml',
        'reports/report_marksheet.xml',
        'wizards/attendees_attendance_wizard_views.xml',
        'wizards/generate_marksheets_views.xml',
    ],
    'license': 'LGPL-3',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
