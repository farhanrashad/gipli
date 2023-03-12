# -*- coding: utf-8 -*-
{
    'name': "Job Position Request",

    'summary': """
    Extra Fields
        """,

    'description': """
        Add Extra fields in Job Position Requests
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Human Resource',
    'version': '14.0.0.3',

    'depends': ['de_job_position_request'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/position_request_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
