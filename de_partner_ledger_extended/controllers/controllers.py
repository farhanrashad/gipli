# -*- coding: utf-8 -*-
# from odoo import http


# class DePartnerLedgerExtended(http.Controller):
#     @http.route('/de_partner_ledger_extended/de_partner_ledger_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_partner_ledger_extended/de_partner_ledger_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_partner_ledger_extended.listing', {
#             'root': '/de_partner_ledger_extended/de_partner_ledger_extended',
#             'objects': http.request.env['de_partner_ledger_extended.de_partner_ledger_extended'].search([]),
#         })

#     @http.route('/de_partner_ledger_extended/de_partner_ledger_extended/objects/<model("de_partner_ledger_extended.de_partner_ledger_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_partner_ledger_extended.object', {
#             'object': obj
#         })
