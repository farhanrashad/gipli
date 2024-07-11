# -*- coding: utf-8 -*-
{
    'name': "Spa Document Formats",

    'summary': "Spa Document Formats",

    'description': """
Spa Document Formats
""",

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale',
        'account',
        'stock',
        'purchase'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'reports/report_account_invoice.xml',
        'reports/report_account_commercial_invoice.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

