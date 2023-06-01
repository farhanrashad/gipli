# -*- coding: utf-8 -*-
{
    'name': "Expense Prepayments",

    'summary': """
        Prepayments to employees for Expenses
        """,
    'description': """
         Expense prepayments app allow to post prepayments to employees and reimburse payments with expenses. This app is integrated and dependent with employee expenses app. 
    """,
    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",
    'category': 'Human Resources/Expenses',
    'version': '16.0.0.4',
    'depends': ['base', 'hr_expense', 'account', 'de_emp_books'],
    'data': [
        'security/ir.model.access.csv',
        'security/expense_advance_security.xml',
        'data/ir_sequence_data.xml',
        'data/mail_data.xml',
        'wizard/expense_prepayment_refuse_reasons_views.xml',
        'views/expense_prepayment_menu.xml',
        'views/expense_prepayments_views.xml',
        'views/hr_expense_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'live_test_url': 'https://www.youtube.com/watch?v=Ymwohz8QawM&t=25s',
    'price': 55,
    'currency': 'USD',
    'images': ['static/description/banner.jpg'],
}
