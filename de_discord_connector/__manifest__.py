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
    'depends': ['mail','base_setup'],

    # always loaded
    'data': [
        'security/discord_security.xml',
        # 'security/ir.model.access.csv',
        'data/res_partner_data.xml',
        'data/res_users_data.xml',
        'data/ir_actions.xml',
        'views/res_config_setting_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

