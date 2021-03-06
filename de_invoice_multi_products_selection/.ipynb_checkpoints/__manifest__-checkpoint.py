# -*- coding: utf-8 -*-
{
    'name': "Add Multiple Products on Invoice",

    'summary': """
Add Multiple Products on invoice""",

    'description': """
Add Multiple Products on Invoice    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/multiple_products_invoice_view.xml',
        'views/account_move_views.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
