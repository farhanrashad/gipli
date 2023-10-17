# -*- coding: utf-8 -*-
{
    'name': "Hunter Connector",

    'summary': """
        Odoo Hunter Integration Module
    """,
    'description': """
        The Odoo Hunter Integration Module is a powerful tool that seamlessly connects your Odoo CRM system with the Hunter app, a leading email outreach and lead generation platform. This integration enables you to find and verify leads effortlessly through domain and company name searches, access contact information, and perform email finder and verification, all while working within your Odoo environment.
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Sales/Marketing',
    'version': '0.3',
    'live_test_url': 'https://youtu.be/kJ_pEsNl0wA',
    'depends': ['crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/instance_views.xml',
        'views/res_config_settings_views.xml',
        'views/hunter_results_views.xml',
        'wizards/api_call_wizard_views.xml',
        'views/crm_lead_views.xml',
        'views/partner_views.xml',
        'wizards/find_email_wizard_views.xml',
        'wizards/convert_data_wizard_views.xml',
    ],
    'assets': {
       'web.assets_backend': [
           'de_hunter_connector/static/src/js/button_search.js',
           'de_hunter_connector/static/src/xml/button_search.xml',
       ],
    },
    'license': 'OPL-1',
    'price': 110,
    'currency': 'USD',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
