# -*- coding: utf-8 -*-
{
    'name': "Openrol - Assignment",

    'summary': """
    Student Assignment
        """,

    'description': """
Openrol - Exam Management App
================================
Features:

    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Sales/Industries',
    'version': '17.0.0.1',
    'live_test_url': 'https://youtu.be/dCpbMEO6EmY',
    'depends': ['de_school'],
    'data': [
        'security/assignment_security.xml',
        'security/ir.model.access.csv',
        'data/assignment_data.xml',
        'data/mail_template_data.xml',
        'views/assignment_menu.xml',
        'views/assignment_views.xml',
        'views/assignment_line_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
