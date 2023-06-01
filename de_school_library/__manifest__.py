# -*- coding: utf-8 -*-
{
    'name': "Library Management ",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Library Management 
    """,

    'author': "Yasir Ali",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'mail', 'resource', 'sale_management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/base_groups.xml',
        'data/data.xml',

        'views/order_view.xml',
        'views/book_type.xml',
        'views/book_category.xml',
        'views/book_author.xml',
        'views/publisher_view.xml',
        'views/product_category_inherit.xml',

        'menu/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
