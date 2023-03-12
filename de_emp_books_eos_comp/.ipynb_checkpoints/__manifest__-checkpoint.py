# -*- coding: utf-8 -*-
{
    'name': "End of Service Compensation",

    'summary': """
    End of Service Compensation
        """,

    'description': """
        End of Service Compensation
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Dynexcel',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['de_emp_books_end_services'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_eos_config_views.xml',
        'views/hr_eos_contract_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
