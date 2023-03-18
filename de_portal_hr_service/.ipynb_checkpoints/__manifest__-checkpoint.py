# -*- coding: utf-8 -*-
{
    'name': "Employee Self Service",

    'summary': """
    Employee Self Service
        """,

    'description': """
        Employee Self Service
    """,
    'author': "dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Human Resources',
    'version': '15.0.2.8',

    'depends': ['portal','hr'],

    'data': [
        #'views/hr_employee_views.xml',

        'security/service_security.xml',
        'security/ir.model.access.csv',
        'views/hr_service_menu.xml',
        'views/hr_service_views.xml',
        'views/res_config_settings.xml',
        'views/hr_services_templates.xml',
        'views/hr_service_web_templates.xml',
        'views/field_variant_views.xml',
       
        
        
    ],
   
    'controllers': [
        'controllers/home_portal_controller.py',
    ],
}
