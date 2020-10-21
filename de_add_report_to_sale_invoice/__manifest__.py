# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo 13 Accounting Add A Report To Sale Invoice',
    'version': '13.0.1.1.2',
    'category': 'Invoicing Management',
    'summary': 'Add a Report to Sale invoice',
    'sequence': '10',
    'author': 'Dynexcel',
    'license': 'LGPL-3',
    'company': 'Dynexcel',
    'maintainer': 'Dynexcel',
    'website': 'http://www.dynexcel.co',
    'depends': ['base' ,'account'],
    'demo': [],
    'data': [
        'reports/report_delivery_note.xml',
        'views/res_partner_view.xml', 
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'qweb': [],
}
