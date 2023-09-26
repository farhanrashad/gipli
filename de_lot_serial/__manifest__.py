# -*- coding: utf-8 -*-
{
    'name': "Bulk Lot and Serial Number Generator",
    'summary': """
        Efficiently Manage Product Serials and Lots
        """,
    'description': """
        The Bulk Lot and Serial Number Generator module is a powerful tool designed to streamline the management of lot and serial numbers for your products and product variants in Odoo. This module simplifies the process of generating large quantities of lot and serial numbers, making it easy to maintain accurate records and meet regulatory compliance requirements.
    """,
    'author': 'Dynexcel',
    'website': 'https://www.dynexcel.com',
    'version': '0.1',
    'category': 'Inventory',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/stock_lot_generate_wizard_views.xml',
        'views/product_views.xml',
        'views/stock_lot_views.xml'
    ],
    'license': 'OPL-1',
    "price": 25,
    "currency": "USD",
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
