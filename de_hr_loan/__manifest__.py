# -*- coding: utf-8 -*-
{
    'name': 'HRMS Loan Management',
    'version': '16.0.1.0.0',
    'summary': 'Manage Loan Requests',
    'description': """
        Helps you to manage Loan Requests of your company's staff.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "Yasir Ali",
    'company': 'www.dynexcel.co',
    'maintainer': 'Yasir Ali',
    'website': "https://www.odynexcel.com",
    'depends': ['base', 'hr', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/loan_data.xml',
        'data/mail_data.xml',
        'views/hr_loan.xml',
        'views/res_config_settings.xml',
        'views/hr_loan_dashboard_views.xml',
        'views/hr_loan_type_views.xml',
        'views/hr_loan_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
