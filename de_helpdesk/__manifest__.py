# -*- coding: utf-8 -*-
{
    'name': "Helpdesk",

    'summary': "Helpdesk",

    'description': """
Helpdesk
""",

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['project'],

    # always loaded
    'data': [
        'security/project_helpdesk_security.xml',
        'security/ir.model.access.csv',
        'data/helpdesk_data.xml',
        'views/helpdesk_menu.xml',
        'views/helpdesk_project_views.xml',
        'views/project_sla_views.xml',
        'views/project_ticket_type_views.xml',
        'views/dashboard_views.xml',
        'views/ticket_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

