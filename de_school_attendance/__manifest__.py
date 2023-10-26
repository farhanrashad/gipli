# -*- coding: utf-8 -*-
{
    'name': "de_school_attendance",

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
    'depends': ['de_school'],

    # always loaded
    'data': [
        'security/attendance_security.xml',
        'security/ir.model.access.csv',
        'views/attendance_menu.xml',
        'views/res_config_settings_views.xml',
        'views/attendance_views.xml',
        'views/attendance_register_views.xml',
        'views/attendance_sheet_views.xml',
        'wizards/mark_attendance_wizard_views.xml',
        'wizards/report_attendance_xlsx_wizard_views.xml',
        'wizards/save_xlsx_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
