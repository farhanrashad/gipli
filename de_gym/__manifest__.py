# -*- coding: utf-8 -*-
{
    'name': "GYM Management",

    'summary': "GYM Management",

    'description': """
GYM Manager
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale',
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['de_subscription','hr'],

    # always loaded
    'data': [
        'security/gym_security.xml',
        'security/ir.model.access.csv',
        'data/gym_data.xml',
        'views/gym_menu.xml',
        'views/res_partner_views.xml',
        #'views/sale_order_views.mxl',
        'views/gym_order_views.xml',
        'views/nutrition_views.xml',
        'views/food_item_views.xml',
        'views/activity_type_views.xml',
        'views/workout_level_views.xml',
        'views/meal_type_views.xml',
        'views/class_type_views.xml',
        'views/class_planning_views.xml',
        'views/class_planning_line_views.xml',
        'views/class_booking_views.xml',
        'views/workout_planning_views.xml',
        'wizards/workout_plan_wizard_views.xml',
        'views/workout_activity_views.xml',
        'views/workout_planning_line_views.xml',
        'wizards/plan_wizard_views.xml',
        'wizards/class_plan_wizard_views.xml',
        'views/nutr_planning_views.xml',
        'wizards/nutr_plan_wizard_views.xml',
    ],
    #'assets': {
    #    'web.assets_backend': [
    #        'de_gym/static/src/js/nutr_schedule_button_calendar.js',
    #        'de_gym/static/src/xml/nutr_schedule_button.xml',
    #    ],
    #},
    'application':True,
}

