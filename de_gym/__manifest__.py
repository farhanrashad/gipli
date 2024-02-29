# -*- coding: utf-8 -*-
{
    'name': "GYM Management",

    'summary': "GYM Management",

    'description': """
GYM Manager
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['de_subscription'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/gym_menu.xml',
        'views/res_partner_views.xml',
        #'views/sale_order_views.mxl',
        'views/gym_order_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

