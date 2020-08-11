# -*- coding: utf-8 -*-
# from odoo import http


# class DeAccountRollpcs(http.Controller):
#     @http.route('/de_account_rollpcs/de_account_rollpcs/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_account_rollpcs/de_account_rollpcs/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_account_rollpcs.listing', {
#             'root': '/de_account_rollpcs/de_account_rollpcs',
#             'objects': http.request.env['de_account_rollpcs.de_account_rollpcs'].search([]),
#         })

#     @http.route('/de_account_rollpcs/de_account_rollpcs/objects/<model("de_account_rollpcs.de_account_rollpcs"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_account_rollpcs.object', {
#             'object': obj
#         })
