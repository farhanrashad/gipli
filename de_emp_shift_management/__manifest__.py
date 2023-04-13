# -*- coding: utf-8 -*-
{
    'name': "de_emp_shift_management",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','resource','utm','portal','report_xlsx','web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/shift_sequence.xml',
        'views/emp_shift_management.xml',
        'views/employee_shift_alloc.xml',
        'views/views.xml',
        'views/templates.xml',
        'reports/report_emp_shifts.xml',
        'wizards/emp_wizard.xml',
        'wizards/emp_shift_report_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
