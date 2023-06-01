# -*- coding: utf-8 -*-
{
    'name': "Hostel Management",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Hostel Management
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

        'views/hostel_views.xml',
        'views/hostel_tag_category.xml',
        'views/product_template_inherit.xml',
        'views/rooms.xml',
        'views/stock_lot.xml',
        'views/hostel_warden.xml',
        'views/stock_location_inherit.xml',
        'views/sale_order_inherit.xml',
        'views/res_partner.xml',
        'views/hostel_type.xml',
        'menu/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
