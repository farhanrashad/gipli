# -*- coding: utf-8 -*-
# from odoo import http


# class DeAccountSaleTarget(http.Controller):
#     @http.route('/de_account_sale_target/de_account_sale_target/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_account_sale_target/de_account_sale_target/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_account_sale_target.listing', {
#             'root': '/de_account_sale_target/de_account_sale_target',
#             'objects': http.request.env['de_account_sale_target.de_account_sale_target'].search([]),
#         })

#     @http.route('/de_account_sale_target/de_account_sale_target/objects/<model("de_account_sale_target.de_account_sale_target"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_account_sale_target.object', {
#             'object': obj
#         })
