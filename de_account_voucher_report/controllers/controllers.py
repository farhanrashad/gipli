# -*- coding: utf-8 -*-
# from odoo import http


# class DeAccountVoucherReport(http.Controller):
#     @http.route('/de_account_voucher_report/de_account_voucher_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_account_voucher_report/de_account_voucher_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_account_voucher_report.listing', {
#             'root': '/de_account_voucher_report/de_account_voucher_report',
#             'objects': http.request.env['de_account_voucher_report.de_account_voucher_report'].search([]),
#         })

#     @http.route('/de_account_voucher_report/de_account_voucher_report/objects/<model("de_account_voucher_report.de_account_voucher_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_account_voucher_report.object', {
#             'object': obj
#         })
