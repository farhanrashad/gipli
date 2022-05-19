# -*- coding: utf-8 -*-

{
    "name": "Partner Ledger Report",
    'version': '14.0.0.1',
    "category": 'Accounting',
    "summary": 'Partner Ledger Report',
    'sequence': 1,
    "description": """"Partner Ledger Report """,
    "author": "Dynexcel",
    "website": "https://www.dynexcel.com",
    'depends': ['account','report_xlsx','de_account_fin_period','de_account_analytic_default'],
    'data': [
        'security/ir.model.access.csv',
        'reports/report_partner_ledger.xml',
        'wizards/report_partner_ledger_wizard_views.xml',
        #'views/view_stock_transfer_order.xml',
        
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}

