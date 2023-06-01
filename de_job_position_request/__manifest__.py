# -*- coding: utf-8 -*-
{
    'name': "Job Position Request",

    'summary': """
        Man Power demand management
        """,

    'description': """
        Job Position Request for Man Power management
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resource',
    'version': '15.0.0.3',

    # any module necessary for this one to work correctly
    'depends': ['hr_recruitment'],

    # always loaded
    'data': [
        #'data/email_template.xml',
        'data/ir_sequence.xml',
        'security/request_security.xml',
        'security/ir.model.access.csv',
        'views/position_request_type_views.xml',
        'views/position_request_views.xml',
    ],
}