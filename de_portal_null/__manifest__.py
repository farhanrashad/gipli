# -*- coding: utf-8 -*-
{
    'name': "Portal",
    'summary': """
        Customize Portal Solution""",
    'description': """
        customize Portal Solution
    """,
    'author': "dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Dynexcel',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
     'license': 'OPL-1',
    'price': 300,
    'currency': 'USD',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
