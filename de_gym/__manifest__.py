# -*- coding: utf-8 -*-
{
    'name': "GYM Management",
    'summary': "GYM Management",
    'description': """
Membership - GYM Management App
================================

Features:

    - Manage member registrations, memberships, and payments effortlessly
    - Create and customize workout plans tailored to individual needs
    - Schedule and organize fitness classes with ease
    - Track attendance and member progress to optimize workouts
    - Monitor equipment maintenance and ensure gym safety
    - Offer nutrition plans and guidance for a holistic approach to fitness
    - Generate reports on membership trends, revenue, and class popularity
    - Integrate with payment systems and fitness tracking apps for seamless operations.
    
""",
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'support': "info@dynexcel.com",
    'category': 'Sales/Subscriptions',
    'version': '17.0.0.1',
    'live_test_url': 'https://youtu.be/_qKgJmMrVq4',
    'depends': ['de_subscription','hr'],
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
        'views/nutr_planning_line_views.xml',
        'wizards/nutr_plan_wizard_views.xml',
    ],
    'license': 'OPL-1',
    'price': 30,
    'currency': 'USD',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}

