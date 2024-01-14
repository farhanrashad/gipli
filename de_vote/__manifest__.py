# -*- coding: utf-8 -*-
{
    'name': "Political",

    'summary': """
    Political
        """,

    'description': """
        Political
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Sales',
    'version': '16.0.0.1',

    'depends': ['base'],

    'data': [
        'security/ir.model.access.csv',
        'security/security_views.xml',
        'views/menu_views.xml',
        'views/res_partner_views.xml',
        'views/member_views.xml',
        'views/party_views.xml',
        'views/constituency_views.xml',
        'views/vote_sign_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
