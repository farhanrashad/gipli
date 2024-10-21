# -*- coding: utf-8 -*-
{
    'name': "Requisition Workflow",

    'summary': """
        Requisition Workflow
        """,

    'description': """
        Requisition Workflow
        - Stages Workflow
        - Security Groups
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Purchase',
    'version': '14.0.0.6',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase_requisition'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/requisition_stage_views.xml',
        'views/purchase_requisition_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
