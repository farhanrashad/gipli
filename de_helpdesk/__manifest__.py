# -*- coding: utf-8 -*-
{
    'name': "Helpdesk",
    'summary': "Monitor, track, and resolve customer issues",
    'description': """
Helpdesk - Ticket Management App
================================

Features:

    - Efficiently resolve customer issues with our comprehensive helpdesk solution
    - Streamline ticket management to prioritize and address inquiries promptly
    - Track the status of customer tickets from submission to resolution
    - Assign tickets to appropriate team members for swift handling
    - Centralize communication channels for seamless interaction with customers
    - Generate reports to analyze performance and identify areas for improvement
    - Integrate with other systems for a holistic approach to customer support management.
    - Install additional features easily.
""",

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Services/Helpdesk',
    'version': '0.1',

    'depends': ['project'],

    # always loaded
    'data': [
        'security/project_helpdesk_security.xml',
        'security/ir.model.access.csv',
        'data/helpdesk_data.xml',
        'data/ir_sequence.xml',
        'data/diget_data.xml',
        'views/helpdesk_menu.xml',
        'views/ticket_tags_views.xml',
        'views/ticket_activity_type_views.xml',
        'views/ticket_stages_views.xml',
        'views/project_team_views.xml',
        'views/project_sla_views.xml',
        'views/ticket_type_views.xml',
        'views/dashboard_views.xml',
        'views/ticket_views.xml',
        'views/helpdesk_portal_templates.xml',
        'views/ticket_reopen_reason_views.xml',
        'wizards/ticket_reopen_wizard_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'OPL-1',
    'price': 50,
    'currency': 'USD',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}

