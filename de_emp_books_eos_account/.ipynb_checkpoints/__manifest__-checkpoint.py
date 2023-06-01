# -*- coding: utf-8 -*-
{
    'name': "End of Service Account",

    'summary': """
    End of Service Account
        """,

    'description': """
        End of Service Account
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resource',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['de_emp_books_eos_comp','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_eos_comp_views.xml',
        'views/hr_eos_contract_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
