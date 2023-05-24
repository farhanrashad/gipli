# -*- coding: utf-8 -*-
{
    'name': "Account Voucher Report",

    'summary': """
              Account Voucher Report
              1-Bill/Invoice Gate Pass report.
              2-Bill report
              3-Cash Receipt Report 
              4- Payment Voucher
              5-Bank Receipt
              6- Bank Payment
        """,

    'description': """
        Account Voucher Report
        1-Bill/Invoice Gate Pass Report.
        2-Bill report
        3- Cash Receipt report
        4- Payment Voucher
        5-Bank Receipt
        6- Bank Payment
        
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '13.0.1.3',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_accountant', 'sh_retail_price_tax'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/account_voucher_report.xml',
        'report/account_voucher_template.xml',
        'report/account_bill_report.xml',
        'report/account_bill_template.xml',
        'report/cash_receipt_report.xml',
        'report/cash_receipt_template.xml',
        'report/cash_payment_report.xml',
        'report/cash_payment_template.xml',
        'report/bank_receipt_voucher_report.xml',
        'report/bank_receipt_voucher_template.xml',
        'report/bank_payment_voucher_report.xml',
        'report/bank_payment_voucher_template.xml',
        'wizard/gatepass_voucher_wizard.xml',
        'wizard/wizard_account_je.xml',
        'report/report_account_wise_purchase_voucher.xml',
        'views/account_move_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
