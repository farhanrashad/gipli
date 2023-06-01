# -*- coding: utf-8 -*-
{
    'name': "Employee Tax Deduction",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Employee Tax Deduction
    """,

    'author': "Yasir Ali",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_contract', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/hr_contract_inherit.xml',
        'views/tax_slabs_view.xml',
        'views/deduction_description_view.xml',
        'views/extra_charges_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
