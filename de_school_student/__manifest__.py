# -*- coding: utf-8 -*-
{
    'name': "Student",

    'summary': """
    School Student
        """,

    'description': """
        School Student
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'CRM/School',
    'version': '15.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['de_school'],

    # always loaded
    'data': [
        'security/student_security.xml',
        # 'security/ir.model.access.csv',
        'views/school_student_menu.xml',
        'views/student_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
