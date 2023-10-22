# -*- coding: utf-8 -*-
{
    'name': "Admission",

    'summary': """
    Admission
        """,

    'description': """
        Admission
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'CRM',
    'version': '16.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['de_school','de_school_team'],

    # always loaded
    'data': [
        'security/admission_security.xml',
        'security/ir.model.access.csv',
        #'data/ir_action_data.xml',
        'data/ir_sequence_data.xml',
        'data/admission_data.xml',
        'views/res_config_settings.xml',
        'views/admission_menu.xml',
        'views/mail_activity_views.xml',
        'views/admission_team_views.xml',
        'views/admission_team_members_views.xml',
        'views/admission_stage_views.xml',
        'views/admission_tag_views.xml',
        'views/admission_register_views.xml',
        'views/admission_views.xml',
        'views/admission_activities_views.xml',
        'views/lead_views.xml',
        'reports/report_admission_views.xml',
        'reports/report_admission_activity_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

    # only loaded in demonstration mode
    #'demo': [
    #    'demo/demo.xml',
    #],
}
