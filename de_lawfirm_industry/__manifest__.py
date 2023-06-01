# -*- coding: utf-8 -*-
{
    'name': "Law Firm Management",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Law Firm Management | Case Management for Lawyers and Law Firms | 
        Law Firm Management System 
        | Legal Case & Matter management | Law Practice Management
    """,

    'author': "Yasir Ali",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'project', 'mail', 'resource', 'calendar'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/base_groups.xml',
        'wizard/close_matter_wizard_view.xml',

        'views/court_view.xml',
        'views/judge_view.xml',
        'views/crime_type_view.xml',
        'views/law_default_task_view.xml',
        'views/law_task_list_view.xml',
        'views/trust_account_view.xml',
        'views/case_matter_view.xml',

        'menus/menus.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
