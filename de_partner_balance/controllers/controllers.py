# -*- coding: utf-8 -*-
# from odoo import http


# class DePartnerBalance(http.Controller):
#     @http.route('/de_partner_balance/de_partner_balance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_partner_balance/de_partner_balance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_partner_balance.listing', {
#             'root': '/de_partner_balance/de_partner_balance',
#             'objects': http.request.env['de_partner_balance.de_partner_balance'].search([]),
#         })

#     @http.route('/de_partner_balance/de_partner_balance/objects/<model("de_partner_balance.de_partner_balance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_partner_balance.object', {
#             'object': obj
#         })
