# -*- coding: utf-8 -*-
{
    'name': "Reports Modifications",

    'summary': """
    Customize reports:
    1. Invoice
        """,

    'description': """
        This module will customize the existing reports.
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','de_partner_extra_fields'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/external_layout_template.xml',
        'views/invoice_report_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
