# -*- coding: utf-8 -*-
{
    'name': "Calendly Connector",

    'summary': "Calendly Connector",

    'description': """
Calendly Connector
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Productivity/Calendar',
    'version': '17.0.0.1',

    'depends': ['calendar'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_setting_views.xml',
        #'views/cal_instance_views.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

