# -*- coding: utf-8 -*-
{
    'name': "Project Services",

    'summary': "Project Services",

    'description': """
Project Services
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Project',
    'version': '17.0.0.1',

    'depends': ['sale_project'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/project_task_views.xml',
        'views/project_views.xml',
        'views/project_milestone_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

