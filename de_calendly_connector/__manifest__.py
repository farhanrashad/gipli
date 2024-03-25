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

    'depends': ['calendar','base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/calendly_data.xml',
        'views/res_config_setting_views.xml',
        'views/cal_instance_views.xml',
        'views/calendar_views.xml',
        'views/calendly_event_type_views.xml',
        'wizards/calendly_cancel_event_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'de_calendly_connector/static/src/js/calendly.js',
            'de_calendly_connector/static/src/xml/calendly.xml',
        ],
    },
}

