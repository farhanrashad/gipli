# -*- coding: utf-8 -*-
{
    'name': "Leave Encashment",
    'summary': """
        Employees can convert unused leave into cash
    """,
    'description': """
        The Leave Encashment module enables employees to request and receive payments in exchange for their unused leave balances. It streamlines the process of converting accrued leave days into monetary compensation, providing employees with a flexible benefit while helping organizations manage their leave policies efficiently.
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Human Resources',
    'version': '0.3',
    'depends': ['base','hr_contract', 'hr_holidays','account','de_hr_workspace_timeoff'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/mail_activity_type_data.xml',
        'views/hr_leave_type_views.xml',
        'views/hr_leave_encash_views.xml',
        'views/workspace_leave_encash_views.xml',
        'wizard/leave_encash_report_wizard_views.xml',
        'reports/leave_encash_report.xml',
        'reports/leave_encash_report_template.xml',
    ],
    'license': 'OPL-1',
    'price': 45,
    'currency': 'USD',
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
