# -*- coding: utf-8 -*-
{
    'name': "KYB",

    'summary': "Know Your Business",

    'description': """
Long description of module's purpose
    """,

    'author': "xpendless",
    'website': "https://www.xpendless.com",

    'category': 'Sales',
    'version': '17.0.0.1',

    'depends': [
        'crm',
        'sale_crm',
        'de_xpendless',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/ir_action_data.xml',
        'data/ir_cron_actions.xml',
        'data/kyb_stage_data.xml',
        'data/kyb_team_data.xml',
        'views/crm_team_views.xml',
        'views/crm_stage_views.xml',
        'views/crm_lead_views.xml',
        'views/res_partner_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

