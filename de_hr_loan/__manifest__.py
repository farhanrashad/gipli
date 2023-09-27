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
    'depends': [
        'base', 'hr', 'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_loan_seq.xml',
        'data/loan_approve_email_temp.xml',
        'views/hr_loan.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
}
