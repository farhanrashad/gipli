# -*- coding: utf-8 -*-
{
    'name': "Subscription",
    'summary': "Subscription Management",
    'description': """
Streamline subscription management with our Odoo module. Effortlessly handle subscriber acquisition, billing cycles, renewals, and more. Optimize revenue streams and enhance customer satisfaction with automated processes and comprehensive tracking. Simplify your subscription-based business operations with Odoo.
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'support': "info@dynexcel.com",
    'category': 'Sales/Subscriptions',
    'version': '17.0.0.3',
    'live_test_url': 'https://youtu.be/_qKgJmMrVq4',
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
    'license': 'OPL-1',
    'price': 50,
    'currency': 'USD',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}

