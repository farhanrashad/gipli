# -*- coding: utf-8 -*-
{
    'name': "Payslip Batches Comparison",

    'summary': """
    Payslip Batches Comparison
        """,

    'description': """
        Payslip - Batches Comparison
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resource',
    'version': '14.0.0.9',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_payroll','de_payroll_taxes'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/payslip_batch_wise_report.xml',
        'report/reports.xml',
        'report/payslip_report_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
