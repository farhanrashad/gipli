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
    'version': '17.0.0.2',
    'depends': [
        'sale_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/menuitems.xml',
        'views/subscription_plan_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'views/subscription_order_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}

