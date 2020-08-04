# -*- coding: utf-8 -*-
# from odoo import http


# class DePartnerLedgerSortbydate(http.Controller):
#     @http.route('/de_partner_ledger_sortbydate/de_partner_ledger_sortbydate/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_partner_ledger_sortbydate/de_partner_ledger_sortbydate/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_partner_ledger_sortbydate.listing', {
#             'root': '/de_partner_ledger_sortbydate/de_partner_ledger_sortbydate',
#             'objects': http.request.env['de_partner_ledger_sortbydate.de_partner_ledger_sortbydate'].search([]),
#         })

#     @http.route('/de_partner_ledger_sortbydate/de_partner_ledger_sortbydate/objects/<model("de_partner_ledger_sortbydate.de_partner_ledger_sortbydate"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_partner_ledger_sortbydate.object', {
#             'object': obj
#         })
