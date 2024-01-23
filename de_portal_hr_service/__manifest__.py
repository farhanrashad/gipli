# -*- coding: utf-8 -*-
{
    'name': "Employee Self Service",

    'summary': """
    Employee Self Service
        """,

    'description': """
        Employee Self Service
    """,
    'author': "dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Human Resources',
    'version': '16.0.5.0',
    'license': 'LGPL-3',
    'live_test_url': 'https://youtu.be/T3ZI7eh0qbg',
    'price': 149,
    'currency': 'USD',

    'depends': ['base','portal','hr','web'],

    'data': [
        'security/service_security.xml',
        'security/ir.model.access.csv',
        'views/hr_service_menu.xml',
        'views/hr_service_views.xml',
        'views/res_config_settings.xml',
        'views/hr_services_templates.xml',
        'views/hr_service_web_templates.xml',
        'views/field_variant_views.xml',
        'views/hr_employee_views.xml',
    ],
    #'assets': {
    #    'web.assets_frontend': [
    #        '/de_portal_hr_service/static/src/js/dynamic_filter.js',
    #    ]
    #},
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
}
