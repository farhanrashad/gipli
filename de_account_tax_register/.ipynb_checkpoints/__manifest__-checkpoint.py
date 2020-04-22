# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2019-today Ascetic Business Solution <www.dynexcel.com>
#

#################################################################################

{
    'name': "Account Tax Register",
    'author': 'Dynexcel',
    'category': 'account',
    'summary': """ Account Tax Register include:
                   1- Sale Register
                   2- Purchase Register
    """,
    'website': 'http://www.dynexcel.com',
    'license': 'AGPL-3',
    'description': """
                Print Tax Register
                1-Invoices which product_id true.
                2-multiple tax on single invoice product.
""",
    'version': '1.1',
    'depends': ['base','account'],
    'data': [
        'wizard/sale_tax_register_views.xml',
        'wizard/purchase_tax_register_views.xml',
        'views/account_tax_register_menu.xml',
        'report/sale_tax_register_report.xml',
        'report/purchase_tax_register_report_view.xml',
        'report/sale_tax_register_template.xml',
        'report/purchase_tax_register_template.xml',
    ],
    'installable': True,
    'images': ['static/description/banner.png'],
    'application': False,
    'auto_install': False,
}
