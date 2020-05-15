# -*- coding: utf-8 -*-
{
    'name': "Tax Register",

    'summary': """
            Account Tax Register 
             """,

    'description': """
            Account Tax Register 
            1- Sale Tax Register
            2- Purchase Tax Register
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'views/account_tax_register_menu.xml',
        'security/ir.model.access.csv',
        'wizard/sale_tax_register_views.xml',
        'wizard/purchase_tax_register_views.xml',
        'report/purchase_tax_register_report_view.xml',
        'report/sale_tax_register_report.xml',
        'report/sale_tax_register_template.xml',
        'report/purchase_tax_register_template.xml',
          ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
