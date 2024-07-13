# -*- coding: utf-8 -*-

{
    'name': "Set Multi Invoices To Draft",
    'summary': """Set Multi Invoices To Draft""",
    'description': """Set Multi Invoices To Draft.""",
    'author': "Ahmed Gaber",
    'license': 'AGPL-3',
    'category': 'account',
    'version': '1.0',
    'depends': ['account'],
    'data': [
        'security/security.xml',
        'views/set_invoice_draft_view.xml',
    ],
    "images": [
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
