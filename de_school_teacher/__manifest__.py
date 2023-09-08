# -*- coding: utf-8 -*-
###############################################################################
# This module has been developed by Dynexcel to enhance the functionality and user experience of the system. Dynexcel, with its commitment to excellence, ensures that this module adheres to the highest standards of quality and performance. We appreciate feedback and suggestions to continually improve our offerings. For any queries or support, please reach out to the Dynexcel team.
###############################################################################
{
    'name': "Techer",
    'summary': """
        Techer
    """,
    'description': """
        Empower educators with the Teacher Module. Consolidate all teacher-related information, from class schedules to professional development records, ensuring organized access and effortless management of their educational roles.
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'CRM/School',
    'version': '16.0.0.1',
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
    'depends': ['de_school','de_school_timetable'],
    'data': [
        'security/teacher_security.xml',
        # 'security/ir.model.access.csv',
        'views/school_teacher_menu.xml',
        'views/teacher_views.xml',
        'views/timetable_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
