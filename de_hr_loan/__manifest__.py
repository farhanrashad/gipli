# -*- coding: utf-8 -*-
{
    'name': 'HRMS Loan Management',
    'version': '16.0.1.0.0',
    'summary': 'Manage Loan Requests',
    'description': """
        Helps you to manage Loan Requests of your company's staff.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "Dynexcel",
    'company': 'www.dynexcel.com',
    'maintainer': 'Dynexcel',
    'website': "https://www.dynexcel.com",
    'depends': ['base', 'hr', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/loan_data.xml',
        'data/mail_data.xml',
        'wizard/loan_reject_wizard_views.xml',
        'wizard/loan_reschedule_wizard_views.xml',
        'wizard/save_xlsx_views.xml',
        'wizard/report_loan_xlsx_wizard_views.xml',
        'views/hr_loan.xml',
        'views/res_config_settings.xml',
        'views/hr_loan_reschedule_views.xml',
        'views/hr_loan_dashboard_views.xml',
        'views/hr_loan_type_views.xml',
        'views/hr_loan_views.xml',
        'reports/report_loan_views.xml',
        
    ],
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
