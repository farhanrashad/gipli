# -*- coding: utf-8 -*-
{
    'name': "Employee Timesheet Management Workspace - Self Service",
    'summary': """
        Self-Service Timesheet Management
    """,
    'description': """
        The Self-Service Timesheet Management sub-module within the employee workspace in Odoo enables users to efficiently record and manage their work hours on specific tasks. Employees can log timesheet entries, associating them with relevant projects and tasks. They can also review their timesheet history, ensuring accurate tracking of their work efforts. This feature empowers employees to actively participate in time management, enhancing project tracking and ensuring transparency in time allocation within the organization.
    """,
    'author': 'Dynexcel',
    'website': 'https://www.dynexcel.com',
    'version': '0.1',
    'category': 'Human Resources',

    # any module necessary for this one to work correctly
    'depends': ['de_hr_workspace','hr_timesheet'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_timehseet_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
