# -*- coding: utf-8 -*-
{
    'name': "Sales Target",

    'summary': """
        Accounting Sales Target
        """,

    'description': """
        Accounting Sales Target
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.5',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_target_views.xml',
        'views/account_move_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
