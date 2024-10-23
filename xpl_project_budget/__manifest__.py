# -*- coding: utf-8 -*-
{
    'name': "Project Budget",

    'summary': "Project budget",

    'description': """
Project Budget
    """,

    'author': "Xpendless",
    'website': "https://www.xpendless.com",

    'category': 'Project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['project','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/project_budget_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

