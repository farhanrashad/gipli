# -*- coding: utf-8 -*-
{
    'name': "Lot Serial",

    'summary': """
        Lot Serial
        """,

    'description': """
        Lot Serial
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Dynexcel',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/stock_lot_generate_wizard_views.xml',
        'views/product_views.xml',
        'views/stock_lot_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
