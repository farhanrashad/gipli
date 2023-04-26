# -*- coding: utf-8 -*-
{
    'name': "Employee Enhancement",

    'summary': """
        Employee  Enhancement""",

    'description': """
        Employee Enhancement
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hr',
    'version': '14.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'account', 'hr_skills', 'hr_contract'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',   
        'views/employee_enhancement_views.xml',
        'views/grade_type_view.xml',
        'views/designation_type_view.xml',
        'views/employee_asset_view.xml',
        'views/resume_views.xml'
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
