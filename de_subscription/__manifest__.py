# -*- coding: utf-8 -*-
{
    'name': "Subscription",
    'summary': "Subscription Management",
    'description': """
Subscription Management
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Sales',
    'version': '17.0.0.3',
    'depends': [
        'sale_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/subscription_data.xml',
        'data/ir_actions_data.xml',
        'views/subscription_menu.xml',
        'views/subscription_templates.xml',
        'views/subscription_plan_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'views/subscription_order_views.xml',
        'views/res_partner_views.xml',
        'views/subscription_close_reason_views.xml',
        'wizards/sale_sub_op_wizard_views.xml',
        'reports/sale_subscription_report_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}

