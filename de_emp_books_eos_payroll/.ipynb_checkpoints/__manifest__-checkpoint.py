# -*- coding: utf-8 -*-
{
    'name': "End of Services - Payroll",

    'summary': """
    Payroll - End of Service
        """,

    'description': """
        Payroll - End of Service
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Human Resource',
    'version': '14.0.0.2',

    'depends': ['de_emp_books_eos_comp','hr_payroll'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_eos_comp_views.xml',
        'views/hr_eos_contract_views.xml',
        'views/hr_payslip_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
