# -*- coding: utf-8 -*-
###############################################################################
# This module has been developed by Dynexcel to enhance the functionality and user experience of the system. Dynexcel, with its commitment to excellence, ensures that this module adheres to the highest standards of quality and performance. We appreciate feedback and suggestions to continually improve our offerings. For any queries or support, please reach out to the Dynexcel team.
###############################################################################
{
    'name': "School Management System",
    'summary': """
        Core Module of School Management System
    """,
    'description': """
        Transform educational administration with the Odoo School Management Core Module. This comprehensive solution centralizes all essential school operations, from student enrollment to staff management, ensuring a seamless and efficient educational environment.
    """,
    'author': "Dynexcel",
    'website': "https://dynexcel.com/",
    'category': 'CRM/School',
    'version': '16.0.0.1',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'depends': ['base','hr'],
    'data': [
        'security/school_security.xml',
        'security/ir.model.access.csv',
        'data/school_data.xml',
        'views/school_menu.xml',
        'views/res_config_settings_views.xml',
        'views/res_company_views.xml',
        'views/resource_calendar_views.xml',
        'views/academic_year_views.xml',
        'views/classroom_views.xml',
        'views/res_partner_views.xml',
        'views/student_views.xml',
        'views/teacher_views.xml',
        'views/course_views.xml',
        'views/batch_views.xml',
        'views/subject_views.xml',
    ],
    'demo': [
        'demo/student_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'de_school/static/src/js/planning_calendar.js',
        ],
        'web.assets_frontend': [
            
        ]
    }
}