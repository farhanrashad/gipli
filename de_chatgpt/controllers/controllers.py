# -*- coding: utf-8 -*-
# from odoo import http


# class DeChatgpt(http.Controller):
#     @http.route('/de_chatgpt/de_chatgpt', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_chatgpt/de_chatgpt/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_chatgpt.listing', {
#             'root': '/de_chatgpt/de_chatgpt',
#             'objects': http.request.env['de_chatgpt.de_chatgpt'].search([]),
#         })

#     @http.route('/de_chatgpt/de_chatgpt/objects/<model("de_chatgpt.de_chatgpt"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_chatgpt.object', {
#             'object': obj
#         })

