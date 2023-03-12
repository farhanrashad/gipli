# -*- coding: utf-8 -*-
{
    'name': "Employee End of Service",

    'summary': """
    Employee End of Services
        """,

    'description': """
        End of Services
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Human Resource',
    'version': '14.0.0.2',

    'depends': ['de_emp_books'],

    'data': [
        'security/hr_eos_security.xml',
        'security/ir.model.access.csv',
        'data/eos_sequence_data.xml',
        'data/mail_data.xml',
        'views/hr_eos_config_views.xml',
        'views/hr_eos_contract_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
