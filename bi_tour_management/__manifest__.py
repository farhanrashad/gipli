# -*- coding: utf-8 -*-
{
    'name': "Tours and Travels, Hotel Management in Odoo",

    'summary': """
       Tours and Travels, Hotel Management in Odoo""",

    'description': """
       Tours and Travels, Hotel Management in Have all Details In Tours Travels and Hotel Management
    """,

    'author': "Yasir Ali",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'account', 'sale_management', 'crm', 'mail', 'resource'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/base_groups.xml',
        # 'wizard/close_matter_wizard_view.xml',
        #
        'views/tour_deduction_policy_view.xml',
        'views/tour_destination_view.xml',
        'views/tour_facility_view.xml',
        'views/tour_package_type_view.xml',
        'views/tour_policy_view.xml',
        'views/tour_season_view.xml',
        'views/hotel_type_view.xml',
        'views/room_type_view.xml',
        'views/service_type.xml',
        'views/hotel_information_view.xml',
        'views/transport_carrier_view.xml',
        'views/travel_class_view.xml',
        'views/transport_information.xml',
        'views/transport_booking_view.xml',
        'views/insurance_type_view.xml',
        'views/insurance_policy_view.xml',
        'views/hotel_reservation_view.xml',
        'views/tour_booking_view.xml',
        'views/tour_program_view.xml',
        'views/visa_cost_view.xml',
        'views/hotel_planner_view.xml',
        'views/travel_details_view.xml',
        'views/tour_service_details_view.xml',
        'views/sale_order_inherit_view.xml',
        'views/agent_commission_view.xml',
        'views/agent_commission_invoice_view.xml',
        'views/tour_preference_view.xml',
        'views/custom_tour_destination_view.xml',
        'views/tour_itinary_view.xml',
        'views/tour_creater_view.xml',
        'views/tour_travel_information.xml',
        'views/tour_cancellation_view.xml',
        #
        'menus/menus.xml',

        'data/sequence.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
