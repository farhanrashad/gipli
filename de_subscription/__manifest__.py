# -*- coding: utf-8 -*-
{
    'name': "Subscription",
    'summary': "Subscription Management",
    'description': """
Subscription Management App
================================

Features:

    - Seamlessly manage subscriptions for products or services
    - Automate subscription renewals and billing processes
    - Track subscriber metrics and analyze subscription trends
    - Offer flexible subscription plans to cater to varying customer needs
    - Provide a user-friendly interface for subscribers to manage their accounts
    - Integrate with payment gateways for secure and convenient transactions
    - Customize pricing and discount options to attract and retain customers
    - Generate reports to assess subscription performance and optimize revenue streams.

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

