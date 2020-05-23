# -*- coding: utf-8 -*-
# from odoo import http


# class DeAccountSaleTeam(http.Controller):
#     @http.route('/de_account_sale_team/de_account_sale_team/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_account_sale_team/de_account_sale_team/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_account_sale_team.listing', {
#             'root': '/de_account_sale_team/de_account_sale_team',
#             'objects': http.request.env['de_account_sale_team.de_account_sale_team'].search([]),
#         })

#     @http.route('/de_account_sale_team/de_account_sale_team/objects/<model("de_account_sale_team.de_account_sale_team"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_account_sale_team.object', {
#             'object': obj
#         })
