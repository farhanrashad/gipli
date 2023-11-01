# -*- coding: utf-8 -*-
{
    'name': "Library",

    'summary': """
    Library Management
        """,

    'description': """
        Library Management
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/Library',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['de_school','sale','stock'],

    # always loaded
    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'data/library_data.xml',
        'views/library_menu.xml',
        'views/genre_views.xml',
        'views/product_views.xml',
        'views/res_partner_views.xml',
        'views/publisher_views.xml',
        'views/author_views.xml',
        'views/sale_order_views.xml',
        'views/student_views.xml',
        'views/teacher_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
