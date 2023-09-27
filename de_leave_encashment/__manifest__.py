# -*- coding: utf-8 -*-
{
    'name': "Leave Encashment",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        HR Leave Encashment
    """,

    'author': "Yasir Ali",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_contract', 'hr_holidays','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/mail_activity_type_data.xml',
        'views/hr_leave_type_views.xml',
        'views/hr_leave_encash_views.xml',
        'views/hr_leave_allocation_view.xml',
        'views/journal_entry_view.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
