# -*- coding: utf-8 -*-
{
    'name': "Social Media Management",

    'summary': "Social Media Management",

    'description': """
Social Media Management
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '17.0.0.1',

    'depends': [
        'web', 
        'mail', 
        'iap', 
        'link_tracker'
    ],

    # always loaded
    'data': [
        'security/social_security.xml',
        'security/ir.model.access.csv',
        'data/social_data.xml',
        'views/social_menu.xml',
        'views/social_media_views.xml',
        'views/social_channel_views.xml',
        'views/social_post_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

