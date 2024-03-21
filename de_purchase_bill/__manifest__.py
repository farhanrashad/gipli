# -*- coding: utf-8 -*-
{
    'name': "Purchase (Downpayment)",
    'summary': """
        Downpayment for purchase
        """,
    'description': """
        This module will add the downpayment functionality in purchase order
    """,
    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",
    'category': 'Purchase',
    'version': '15.0.0.5',
    'depends': ['base','purchase','account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_advance_payment_inv.xml',
        'views/purchase_order_views.xml',
        'views/res_config_setting_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'live_test_url': 'https://youtu.be/iziZarRF3D0',
    'price': 55,
    'currency': 'USD',
    'images': ['static/description/banner.png'],
}
