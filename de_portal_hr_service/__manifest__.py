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
    'version': '16.0.4.2',
    'license': 'LGPL-3',
    'live_test_url': 'https://youtu.be/f_uSGd3qJNU',
    'price': 149,
    'currency': 'USD',

    'depends': ['portal','hr'],

    'data': [
        'security/service_security.xml',
        'security/ir.model.access.csv',
        'views/hr_service_menu.xml',
        'views/hr_service_views.xml',
        'views/res_config_settings.xml',
        'views/hr_services_templates.xml',
        'views/hr_service_web_templates.xml',
        'views/field_variant_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'de_portal_hr_service/static/src/js/auto_fill_script.js',
            'de_portal_hr_service/static/src/js/datatable.js',
            'de_portal_hr_service/static/src/js/dynamic_form.js',
            'de_portal_hr_service/static/src/js/items_datatable.js',
            'de_portal_hr_service/static/src/js/jquery.js',
            'de_portal_hr_service/static/src/js/main_datatable.js',
            'de_portal_hr_service/static/src/js/select_two.js',
            'de_portal_hr_service/static/src/js/sweetalert.js',
            'de_portal_hr_service/static/src/js/js_export/*',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
}
