# -*- coding: utf-8 -*-
{
    'name': "Library",

    'summary': """
    Library Management
        """,

    'description': """
        Library Management
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/Library',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['de_school','sale','stock','web'],

    # always loaded
    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'data/library_data.xml',
        'views/library_menu.xml',
        'views/genre_views.xml',
        'views/fee_periods_views.xml',
        'views/product_views.xml',
        'views/res_partner_views.xml',
        'views/publisher_views.xml',
        'views/author_views.xml',
        'views/sale_order_views.xml',
        'views/student_views.xml',
        'views/teacher_views.xml',
        'views/agreement_views.xml',
        'wizards/fee_configurator_views.xml',
        'wizards/order_processing_views.xml',
        'reports/report_library_views.xml',
    ],
    'js': [
        'de_school_library/static/src/js/library_fee_config_wizard.js',
    ],
    'assets': {
       'web.assets_backend': [
           #'de_school_library/static/src/js/library_fee_config_wizard.js',
           #'de_school_library/static/src/js/library_fee_config_wizard.js',
           'de_school_library/static/src/**/*',
       ],
    },
}
