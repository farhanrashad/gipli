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
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

