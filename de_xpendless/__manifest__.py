# -*- coding: utf-8 -*-
{
    'name': "Xpendless",

    'summary': "Xpendless - Base",

    'description': """
Base module of Xpendless Integration
""",

    'author': "Xpendless",
    'website': "https://www.xpendless.com",

    'category': 'Sales',
    'version': '17.0.0.3',

    'depends': ['base'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu_views.xml',
        'views/instance_views.xml',
        'views/res_partner_views.xml',
        'views/expense_views.xml',
        'wizards/ops_wizard_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

