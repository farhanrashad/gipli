# -*- coding: utf-8 -*-
# from odoo import http


# class DeAccountSequence(http.Controller):
#     @http.route('/de_account_sequence/de_account_sequence/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_account_sequence/de_account_sequence/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_account_sequence.listing', {
#             'root': '/de_account_sequence/de_account_sequence',
#             'objects': http.request.env['de_account_sequence.de_account_sequence'].search([]),
#         })

#     @http.route('/de_account_sequence/de_account_sequence/objects/<model("de_account_sequence.de_account_sequence"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_account_sequence.object', {
#             'object': obj
#         })
