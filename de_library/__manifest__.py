# -*- coding: utf-8 -*-
{
    'name': "Library Management",
    'summary': """
    Efficient Library Management Made Easy
        """,
    'description': """
Library Management App
================================

Features:

 - Comprehensive book cataloging to manage and organize your entire library collection efficiently.
 - Author and publisher management to maintain detailed records.
 - Flexible book rental pricing to customize rental prices for different books.
 - Circulation agreements to handle circulation seamlessly.
 - Efficient issuance and return processes to streamline book transactions.
 - Detailed books movement analysis report to provide comprehensive insights. 
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'support': "info@dynexcel.com",
    'live_test_url': 'https://youtu.be/PJEkGzyCQ2Q',
    'category': 'Sales/Library',
    'version': '17.0.0.3',
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
        'reports/report_library_views.xml',
    ],
    'js': [
        #'de_school_library/static/src/js/library_fee_config_wizard.js',
    ],
    'assets': {
       'web.assets_backend': [
           #'de_school_library/static/src/**/*',
       ],
    },
    'license': 'OPL-1',
    'price': 75,
    'currency': 'USD',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
