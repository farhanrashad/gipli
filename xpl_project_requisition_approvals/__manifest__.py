# -*- coding: utf-8 -*-
{
    'name': "Requisition Approvals",

    'summary': "Requisition Approvals",

    'description': """
Long description of module's purpose
    """,

    'author': "Xpendless",
    'website': "https://www.xpendless.com",

    'category': 'Project/Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['project','purchase_requisition'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_requisition_views.xml',
        'views/purchase_requisition_approval_views.xml',
        'views/approvals_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

