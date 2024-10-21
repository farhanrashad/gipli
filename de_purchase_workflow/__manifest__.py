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

    'author': "farhan",
    'website': "https://www.farhan.com",
    'category': 'Purchase',
    'version': '18.0.0.1',

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
