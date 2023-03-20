# -*- coding: utf-8 -*-
{
    'name': "HR Service Report Designer",

    'summary': """
    HR Service Report Designer
        """,

    'description': """
        HR Service Report Designer
    """,
    'author': "dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Human Resources',
    'version': '15.0.0.3',
    'license': 'LGPL-3',
    'live_test_url': 'https://youtu.be/f_uSGd3qJNU',
    'price': 39,
    'currency': 'USD',
    
    'depends': ['portal','hr','de_portal_hr_service'],

    'data': [
        #'security/service_security.xml',
        'security/ir.model.access.csv',
        'views/hr_service_report_views.xml',
        'views/hr_reports_templates.xml',
        'views/hr_report_web_templates.xml',  
        'views/hr_report_result.xml',  
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.png'],
   
}
