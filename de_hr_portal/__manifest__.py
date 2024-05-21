# -*- coding: utf-8 -*-
{
    'name': "Portal Extention",

    'summary': "Portal Extention",

    'description': """
Portal Extentsion
""",
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Human Resource',
    'version': '17.0.0.1',
    'depends': ['hr'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'OPL-1',
    'price': 149,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
}

