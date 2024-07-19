# -*- coding: utf-8 -*-
{
    'name': "Website Helpdesk",
    'summary': "This module enables website users to generate helpdesk tickets directly.",
    'description': """
This module allows users to easily generate helpdesk tickets directly from the website, streamlining the support process. It integrates seamlessly with existing helpdesk systems, ensuring efficient ticket management and prompt responses to user inquiries.
""",
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Services/Helpdesk',
    'version': '17.0.0.3',
    'depends': [
        'de_helpdesk',
        'website',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/helpdesk_project_views.xml',
        'views/helpdesk_portal_templates.xml',
    ],
    'license': 'OPL-1',
    'price': 10,
    'currency': 'USD',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': False,
    'auto_install': False,
}

