# -*- coding: utf-8 -*-
{
    'name': "Political",

    'summary': """
    Political
        """,

    'description': """
        Political
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Sales',
    'version': '16.0.0.1',

    'depends': ['base'],

    'data': [
        # 'security/ir.model.access.csv',
        'security/security_views.xml',
        'views/menu_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
