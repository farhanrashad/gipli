# -*- coding: utf-8 -*-
{
    'name': "Apollo Connector",

    'summary': """
        Odoo Apollo Integration
    """,

    'description': """
        The Odoo Apollo Integration module seamlessly connects your Odoo CRM with Apollo, enabling streamlined prospecting and lead enrichment. Search and import leads from Apollo, enrich lead data, synchronize information in real-time, and automate tasks, all within your Odoo CRM. Elevate your lead management with accurate, up-to-date data and efficient workflows.
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Sales/Marketing',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['crm'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/apollo_data.xml',
        'views/apollo_views.xml',
        'views/apollo_instance_views.xml',
        'views/res_partner_category_views.xml',
        'views/res_partner_views.xml',
        'views/crm_lead_views.xml',
        'views/crm_tag_views.xml',
        'views/crm_stage_views.xml',
        'wizards/people_search_wizard_views.xml',
        'wizards/companies_search_wizard_views.xml',
        'views/apl_people_views.xml',
        'views/apl_companies_views.xml',
        'wizards/send_data_wizard_views.xml',
    ],
    'assets': {
       'web.assets_backend': [
           'de_apollo_connector/static/src/js/button_search.js',
           'de_apollo_connector/static/src/xml/button_search.xml',
       ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
