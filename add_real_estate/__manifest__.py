# -*- coding: utf-8 -*-
{
    'name': "add_real_estate",
    'version': '17.0.0.0',
    'depends': ['base', 'project', 'product', 'web', 'analytic', 'account', 'sale',
                 'account_batch_payment',
                 'account_check_printing',
                 'account_reports',
                 'hr_recruitment',
                'contacts'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/rule.xml',
        'security/ir.model.access.csv',
        'views/menus.xml',

        'wizard/merge_view.xml',
        'wizard/cancel_res_views.xml',
        'wizard/change_property_price_wiz.xml',
        'wizard/create_payment_lines.xml',
        'wizard/merge_partner.xml',
        'wizard/address_fill_payment_lines_wizard.xml',
        'wizard/delivery_to_customer_wiz.xml',
        'wizard/commission_account_wizard.xml',
        'wizard/multi_collection_wiz.xml',
        'wizard/warning_popUp.xml',
        'wizard/edit_analytic_account_after_post.xml',
        'data/sequence.xml',


        #master
        'views/master/company.xml',
        'views/master/custom_tables_view.xml',
        'views/master/city_country_views.xml',
        'views/master/res_user_views.xml',
        'views/master/company_team_views.xml',
        'views/master/partners_view.xml',
        # real
        'views/real/property_view.xml',
        'views/real/image_view.xml',
        'views/real/history_views.xml',
        'views/real/action_server_view.xml',
        'views/real/request_reservation.xml',
        'views/real/res_reservation.xml',
        'views/real/release_unit.xml',
        'views/real/transfer_unit.xml',
        'views/real/contract_view.xml',
        'views/real/Accessories.xml',
        'views/real/commission_view.xml',
        'views/real/unit_factor.xml',
        'views/real/contract_reservation.xml',
        'views/real/pol_com.xml',
        # Project
        'views/project/project_views.xml',
        'views/project/phase_views.xml',

        # account
        'views/account/address_pay_strategy.xml',
        'views/account/customer_payment.xml',
        'views/account/payment_view_inherit.xml',
        'views/account/payement_strg.xml',
        'views/account/vendor_normal_deposit.xml',
        'views/account/payment_line_type_view.xml',
        'views/account/description_payment.xml',
        'views/account/account_account.xml',
        'views/account/bank.xml',
        'views/account/payment_not_received.xml',
        'views/account/real_partner_ledger.xml',
        'views/account/tax.xml',
        'views/account/payment_search.xml',
        'views/account/payment_tree.xml',
        'views/account/notify_disc.xml',
        'views/account/journal.xml',


        #  'views/templates.xml',
        'report/add_move_report.xml',
        'report/report_header_footer_base.xml',
        'report/report_reservation.xml',
        'report/report_reservation_base.xml',
        'report/report_sample.xml',
        'report/report_payment_strg_request.xml',
        'report/report_saledetails_test.xml',
        'report/report_payment_base.xml',
        'report/report_customer_payment_base.xml',
        'report/contract_reservation.xml',
        'report/invoice.xml',
        'report/payment_all.xml',
        'report/unit_transfer.xml',
        'report/notify_discount_report.xml',
    ],
    'assets': {
    'web.assets_backend': [
        'add_real_estate/static/src/xml/**/*',
    ]
    }

    # 'qweb': [
    #         "static/src/xml/pay.xml",
    # ]

}
