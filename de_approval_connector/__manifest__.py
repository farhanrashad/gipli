# -*- coding: utf-8 -*-
{
    'name': "Approval Connector",
    'summary': """
        Integration with other Models
        """,
    'description': """
        Approval Connector
         - Integration with other models
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Extra Tools',
    'version': '14.0.0.1',

    'depends': ['base','approvals'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/approval_category_views.xml',
        'views/approval_request_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
