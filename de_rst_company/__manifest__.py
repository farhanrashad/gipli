# -*- coding: utf-8 -*-
{
    'name': "de_rst_company",

    'summary': """
       company specific domain""",

    'description': """
        company specific domain on partner and product
    """,

    'author': "Dynexcel",
   
    'category': 'Uncategorized',
    'version': '13.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','sale','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        # 'security/security.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
