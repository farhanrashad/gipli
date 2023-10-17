# -*- coding: utf-8 -*-
{
    'name': "School Fees",

    'summary': """
    Fee Management
        """,

    'description': """
        Fees Managment
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Dynexcel',
    'version': '16.0.0.2',
    'installable': True,
    'application': True,
    # any module necessary for this one to work correctly
    'depends': ['de_school','account','de_school_enrollment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/fee_data.xml',
        'data/feeslip_sequence.xml',
        'views/fees_menu.xml',
        'views/fee_category_views.xml',
        'views/fee_rule_views.xml',
        'views/fee_struct_views.xml',
        'views/feeslip_input_type_views.xml',
        'views/feeslip_views.xml',
        'wizard/feeslip_by_students_views.xml',
        'views/feeslip_run_views.xml',
        'reports/feeslip_report_template.xml',
        'reports/feeslip_report.xml',
        'reports/feeslip_report_views.xml',
        'wizard/report_feeslip_xlsx_wizard_views.xml',
        'views/feeslip_schedule_views.xml',
        'wizard/feeslip_schedule_wizard_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
