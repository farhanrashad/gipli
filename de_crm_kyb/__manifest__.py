# -*- coding: utf-8 -*-
{
    'name': "KYB",

    'summary': "Know Your Business",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/ir_action_data.xml',
        'views/crm_team_views.xml',
        'views/crm_stage_views.xml',
        'views/crm_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

