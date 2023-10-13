# -*- coding: utf-8 -*-
{
    'name': "Payment Allocation",

    'summary': """
        Payment Allocation - IGT Version
        1- Invoice Payment Allocation
        """,

    'description': """
        Payment Allocation
        1- Invoice Payment Allocation
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '14.0.6.2',

    # any module necessary for this one to work correctly
    'depends': ['analytic','account'],

    # always loaded
    'data': [
        #'data/ir_server_actions_views.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/account_account_views.xml',
        'views/account_journal_views.xml',
        'views/account_payment_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
