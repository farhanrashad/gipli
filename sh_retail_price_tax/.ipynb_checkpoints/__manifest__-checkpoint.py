# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Dynexcel Retail Price Tax Calculation",
    "author" : "Dynexcel",
    "website": "http://www.dynexcel.com",
    "support": "support@dynexcel.com",
    "category": "Account",
    "summary": "",
    "description": """

                    """,
    "version":"13.0.4",
    "depends" : ["base","sale_management","account"],
    "application" : True,
    "data" : [
            'views/sh_product_view.xml',
            'views/sh_account_move.xml',
            ],
    "images": ["static/description/background.png", ],
    "auto_install":False,
    "installable" : True,
}
