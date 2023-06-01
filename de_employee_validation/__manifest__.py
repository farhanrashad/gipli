# -*- coding: utf-8 -*-
{
    'name': "Employee Validation",

    'summary': """
        Employee Validation
        """,

    'description': """
        Employee Validation:-
        Add Contact Stages
        1. Draft
        2. To Approve
        3. Approved
        Only Approved contact shall be accessible at pages
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Marketing',
    'version': '14.0.0.1',
    'depends': ['base','hr'],
    'data': [
        # 'security/ir.model.access.csv',
        'security/employee_security.xml',
        'views/hr_employee_views.xml',
        
    ],
    "price": 25,
    "currency": "USD",
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/tryZg1W3OnQ',
    "images":['static/description/banner.jpg'],
}
