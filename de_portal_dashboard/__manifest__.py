# -*- coding: utf-8 -*-
{
    'name': "Portal Dashboard",

    'summary': """
    Portal Dashbaord
        """,

    'description': """
        Portal Dashbaord
    """,

    'author': "dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'portal',
               ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_menu.xml',
        'views/dashboard_views.xml',
        'views/portal_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
