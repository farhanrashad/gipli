# -*- coding: utf-8 -*-
# from odoo import http


# class DeReportPartnerBal(http.Controller):
#     @http.route('/de_report_partner_bal/de_report_partner_bal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_report_partner_bal/de_report_partner_bal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_report_partner_bal.listing', {
#             'root': '/de_report_partner_bal/de_report_partner_bal',
#             'objects': http.request.env['de_report_partner_bal.de_report_partner_bal'].search([]),
#         })

#     @http.route('/de_report_partner_bal/de_report_partner_bal/objects/<model("de_report_partner_bal.de_report_partner_bal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_report_partner_bal.object', {
#             'object': obj
#         })
