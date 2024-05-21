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
    'category': 'Sales/Library',
    'version': '17.0.0.2',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    
    'depends': [
        'sale_stock',
        'sale_management',
    ],
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
        'views/sale_order_line_views.xml',
        'views/member_views.xml',
        'views/agreement_views.xml',
        'wizards/fee_configurator_views.xml',
        'wizards/order_processing_views.xml',
        #'reports/report_library_views.xml',
    ],
    'js': [
        'de_school_library/static/src/js/library_fee_config_wizard.js',
    ],
    'assets': {
       'web.assets_backend': [
           #'de_school_library/static/src/**/*',
       ],
    },
}
