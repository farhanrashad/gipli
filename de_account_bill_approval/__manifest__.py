# -*- coding: utf-8 -*-
{
    'name': "Account Bill Approval",

    'summary': """
        Account Bill Approval""",

    'description': """
         Account Bill Approval 
         """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/vendor_bill_approval_view.xml',
        'views/vendor_bill_state_view.xml',
        'views/vendor_bill_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
