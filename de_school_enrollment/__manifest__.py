# -*- coding: utf-8 -*-
###############################################################################
# This module has been developed by Dynexcel to enhance the functionality and user experience of the system. Dynexcel, with its commitment to excellence, ensures that this module adheres to the highest standards of quality and performance. We appreciate feedback and suggestions to continually improve our offerings. For any queries or support, please reach out to the Dynexcel team.
###############################################################################
{
    'name': "Enrollment",

    'summary': """
    Student Enrollment
        """,
    'description': """
        Enrollment
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'School',
    'version': '16.0.0.1',
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
    'depends': ['de_school','sale'],
    'data': [
        'security/enrollment_security.xml',
        'security/ir.model.access.csv',
        'views/enrollment_menu.xml',
        'views/enrol_order_template_views.xml',
        'views/product_views.xml',
        'views/sale_views.xml',
        'views/enrollment_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
