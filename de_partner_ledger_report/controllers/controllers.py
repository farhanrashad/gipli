# -*- coding: utf-8 -*-
# from odoo import http


# class DePartnerLedgerReport(http.Controller):
#     @http.route('/de_partner_ledger_report/de_partner_ledger_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_partner_ledger_report/de_partner_ledger_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_partner_ledger_report.listing', {
#             'root': '/de_partner_ledger_report/de_partner_ledger_report',
#             'objects': http.request.env['de_partner_ledger_report.de_partner_ledger_report'].search([]),
#         })

#     @http.route('/de_partner_ledger_report/de_partner_ledger_report/objects/<model("de_partner_ledger_report.de_partner_ledger_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_partner_ledger_report.object', {
#             'object': obj
#         })
