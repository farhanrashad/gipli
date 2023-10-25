# -*- coding: utf-8 -*-
{
    'name': "de_school_attendance",

    'summary': """
       School Attendance """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Dynexcel(erum)",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','de_school','resource','portal'],

    # always loaded
    'data': [
            'security/ir.model.access.csv',
            'data/sequence.xml',
            'views/school_attendance.xml',
            'views/attendance_settings.xml',
            'wizards/wizard_attendance_registr.xml',
            'wizards/report_wizard_attendance_details.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
