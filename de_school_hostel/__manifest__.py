# -*- coding: utf-8 -*-
{
    'name': "Openrol - Hostel",

    'summary': "Hostel Management App",

    'description': """
Long description of module's purpose
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'School/Industries',
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'de_school'
    ],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hostel_menu.xml',
        'views/unit_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

