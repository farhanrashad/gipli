# -*- coding: utf-8 -*-
{
    'name': "Discord Connector",

    'summary': "Discord Connector",

    'description': """
Discord Connector
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Discuss',
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_setting_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

