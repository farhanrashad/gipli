# -*- coding: utf-8 -*-
{
    'name': "Purchase Budget",

    'summary': """
        Purchase Budget 
        """,

    'description': """
Quantative Purchase Budget
=======================================
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '18.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order_views.xml',
        'views/purchase_budget_views.xml',
        'views/purchase_budget_category_views.xml',
        'report/purchase_budget_report_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
