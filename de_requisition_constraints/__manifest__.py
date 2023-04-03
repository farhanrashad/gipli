# -*- coding: utf-8 -*-
{
    'name': "Requisition Constraints",

    'summary': """
        Requisition Constraints
        """,

    'description': """
        Requisition Constraints
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Purchase',
    'version': '14.0.0.3',

    # any module necessary for this one to work correctly
    'depends': ['de_requisition_workflow'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_requisition_views.xml',
        'views/requisition_type_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
