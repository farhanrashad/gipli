# -*- coding: utf-8 -*-
{
    'name': "Report Builder",

    'summary': "Empower Your Reporting Workflow with Odoo Report Builder",

    'description': """
Report Builder
================================
Odoo's Report Builder module revolutionizes data reporting by offering a user-friendly interface for creating, customizing, and analyzing reports effortlessly. With intuitive tools and powerful capabilities, users can transform raw data into actionable insights, enabling informed decision-making across the organization.
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Extra Tools/Sales/Accounting/Project',
    'live_test_url': 'https://youtu.be/bpUTMHdUwL8',
    'version': '17.0.0.3',
    'depends': ['base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/report_builder_menu.xml',
        'views/report_config_views.xml',
        'wizards/custom_report_template.xml',
        'wizards/action_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'de_report_builder/static/src/js/report_action.js',
        ],
    },
    'license': 'OPL-1',
    'price': 150,
    'currency': 'USD',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}

