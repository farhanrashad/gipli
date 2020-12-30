# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "Customer Cash Collection",
    "summary": 'Customer Cash Collection',
    "sequence": 1,
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    "version": '13.0.1.1',
    "depends": ['base','account','account_accountant'],
    "data": [
        'security/ir.model.access.csv',
        'views/cash_collection_view.xml',
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
