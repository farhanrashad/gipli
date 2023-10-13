# -*- coding: utf-8 -*-
{
    'name': "Hunter Connector",

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
    'application': False,
    'auto_install': False,
}
