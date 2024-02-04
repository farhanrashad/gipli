# -*- coding: utf-8 -*-
{
    'name': "Employee Self Service",

    'summary': "Employee Self Service",

    'description': """
Employee Self Service
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Human Resources',
    'version': '17.0.1.5',
    'license': 'LGPL-3',
    'live_test_url': 'https://youtu.be/T3ZI7eh0qbg',
    'price': 149,
    'currency': 'USD',
    
    'depends': ['base','portal','hr','web'],

    # always loaded
    'data': [
        'security/service_security.xml',
        'security/ir.model.access.csv',
        'views/hr_service_menu.xml',
        'views/hr_service_views.xml',
        'views/res_config_settings.xml',
        'views/hr_employee_views.xml',
        'views/field_variant_views.xml',
        'views/hr_services_templates.xml',
        'views/hr_service_web_form_templates.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
}

