# -*- coding: utf-8 -*-
{
    'name': "Applolo Connector",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['crm'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/apollo_views.xml',
        'views/apollo_instance_views.xml',
        'views/res_partner_views.xml',
        'views/crm_lead_views.xml',
        'wizards/people_search_wizard_views.xml',
        'wizards/companies_search_wizard_views.xml',
        'views/apl_people_results_views.xml',
        'views/apl_companies_results_views.xml',
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
