# -*- coding: utf-8 -*-
{
    'name': "Customization",

    'summary': """
        Modifications in built in modules""",

    'description': """
        This module is for customization purposes.
    """,

    'author': "Yaseen Malik",
    'website': "http://www.dynexcel.co",

    'category': 'Customization',
    'version': '0.1',

    'depends': ['base', 'stock', 'mrp', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/product_ext.xml',
    ],
}