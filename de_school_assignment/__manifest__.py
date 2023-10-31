# -*- coding: utf-8 -*-
{
    'name': "Assignment",

    'summary': """
    Student Assignment
        """,

    'description': """
        Student Assignment
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'School',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['de_school'],

    # always loaded
    'data': [
        'security/assignment_security.xml',
        'security/ir.model.access.csv',
        'views/assignment_menu.xml',
        'views/assignment_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
