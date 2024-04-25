# -*- coding: utf-8 -*-
{
    'name': 'Zoom Meeting Integration',
    'summary': 'Multi User Zoom Meeting Integration',
    'description': """
    This Zoom integration enables users to schedule instant Zoom meetings with customers. users can use their Zoom login credentials and host concurrent Zoom meetings with customers.

    """,
    'category': 'Discuss',
    'author': 'Dynexcel',
    'version': '17.0.0.1',
    'price': 149,
    'currency': 'USD',
    'website': 'https://www.dynexcel.com',
    'images': ['static/description/banner.gif'],
    'depends': ['calendar', 'mail'],
    'data': [
            #'security/ir.model.access.csv',
            #'data/external_user_mail_data.xml',
            #'data/mail_data.xml',
            #'view/users_views.xml',
            #'view/calendar_views.xml',
            #'view/company_views.xml',
            #'view/calendar_templates.xml',
            #'wizard/new_zoom_user.xml',
            #'wizard/message_wizard.xml',

    ],
    'external_dependencies': {
        'python': ['zoomus'],
    },
}
