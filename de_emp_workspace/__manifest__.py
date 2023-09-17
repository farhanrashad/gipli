# -*- coding: utf-8 -*-
{
    'name': 'Employee Workspace',
    'version': '1.4',
    'category': 'Human Resources',
    'summary': 'Employee Self-Service Portal',
    'description': """
        The "Employee Workspace" module is a comprehensive solution that enhances Odoo's Human Resources capabilities by providing employees with a powerful self-service portal. This portal empowers employees to manage various HR-related tasks efficiently, thereby reducing administrative overhead and enhancing overall organizational productivity.

        Key Features:
        - **Employee Profiles:** Employees can view and update their personal information, contact details, and emergency contacts.
        - **Time-Off Requests:** Streamline time-off requests and approvals. Employees can submit leave requests, view their leave balances, and track the status of their requests.
        - **Document Management:** Upload and access important documents such as contracts, certificates, and identification documents.
        - **Payroll Information:** Access salary details, payslips, and tax information securely.
        - **Performance Evaluations:** Review performance feedback and participate in self-assessments.
        - **Training and Development:** Enroll in training programs and courses to enhance skills and career development.
        - **Announcements:** Stay informed about company news, events, and announcements.
        
        Author: Dynexcel (https://www.dynexcel.com)
        
        This module is designed to improve employee engagement, streamline HR processes, and foster a culture of transparency within the organization. It is fully integrated with Odoo's core HR functionalities, ensuring data accuracy and consistency.

        Installation Instructions:
        1. Install this module via the Odoo Apps interface.
        2. Ensure that the 'base' and 'hr' modules are already installed and up to date.
        3. Configure access rights for user groups to control who can access the Employee Workspace.

        For support and inquiries, please visit our website: https://www.dynexcel.com/contact

        Note: This module may require additional customization to meet the specific needs of your organization. Feel free to contact us for customization services.
    """,
    'author': 'Dynexcel',
    'website': 'https://www.dynexcel.com',
    'depends': ['base', 'hr','hr_contract','project','hr_timesheet','hr_attendance','hr_expense','hr_holidays'],
    'data': [
        'security/security_group.xml',
        'security/ir.model.access.csv',
        'views/workspace_menu.xml',
        'views/hr_employee_views.xml',
        'views/hr_contract_views.xml',
        'views/project_views.xml',
        'views/hr_attendance_views.xml',
        'views/hr_expense_views.xml',
        'views/hr_holidays_views.xml',
    ],
    'license': 'OPL-1',
    "price": 25,
    "currency": "USD",
    'images': ['static/description/banner.png'],  # Specify the path to your banner image
    'installable': True,
    'application': True,
    'auto_install': False,
}
