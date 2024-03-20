# -*- coding: utf-8 -*-
{
    'name': "Payment Automation",

    'summary': "Payment Run - Payment Automation Program",

    'description': """
Payment run program streamlines financial operations by automating the collection and disbursement of payments. It allows businesses to schedule and execute payment runs efficiently, ensuring timely payments to vendors and seamless collection from customers. Say goodbye to manual payment processing hassles and embrace the convenience and accuracy of automated payment management with Odoo's robust module.
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_run_views.xml',
        'views/payment_run_line_views.xml',
        'views/res_partner_views.xml',
        'reports/ir_actions_report.xml',
        'reports/ir_actions_report_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

