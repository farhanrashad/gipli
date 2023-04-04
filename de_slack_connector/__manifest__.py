# -*- coding: utf-8 -*-
{
    'name': "Slack Integration",

    'summary': """Slack Odoo Integration""",

    'description': """Odoo is a fully integrated suite of business modules that encompass the traditional ERP functionality. Odoo Slack allows you to send updates on your Slack.
    """,
    
    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",
 
   
    'category': 'project',
    'version': '14.0.0.0.0',
    'price': '',
    'currency': 'EUR',
     "license": "",


    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],
    'images': [
        'static/description/banner1.gif',
    ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/de_slk_settings_view.xml',
        'views/de_temp_view.xml',
        'views/de_user_view.xml',
        'data/scheduler.xml',

    ],

    'external_dependencies': {'python': ['slackclient']},

    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
