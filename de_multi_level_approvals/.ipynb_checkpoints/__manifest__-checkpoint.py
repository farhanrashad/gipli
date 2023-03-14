# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "Multi Level Approvals",
    "summary": 'Multiple Level Approvals ',
    "sequence": 1,

    "author": "Dynexcel",
    "website": "https://www.dynexcel.com",
    "version": '15.0.0.9',

    "depends": ['base','approvals'],
    "data": [
        'security/ir.model.access.csv',
        'views/approval_category_views.xml',
        'views/approval_request_views.xml',
    ],

    "installable": True,
    "application": False,
    "auto_install": False,
}
