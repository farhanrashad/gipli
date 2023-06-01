# -*- coding: utf-8 -*-
{
    'name': "Employee Shit Management",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Employee shift Management
    """,

    'author': "Yasir Ali",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'mail', 'resource'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/base_groups.xml',

        'views/shift_request_view.xml',
        'views/shift_request_to_approve_view.xml',
        'views/all_shift_request_view.xml',
        'views/shift_type.xml',
        'views/hr_employee_view.xml',

        'report/report.xml',
        'report/shift_request_template.xml',
        'data/sequence.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
