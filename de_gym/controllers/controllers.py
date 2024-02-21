# -*- coding: utf-8 -*-
# from odoo import http


# class DeGym(http.Controller):
#     @http.route('/de_gym/de_gym', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_gym/de_gym/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_gym.listing', {
#             'root': '/de_gym/de_gym',
#             'objects': http.request.env['de_gym.de_gym'].search([]),
#         })

#     @http.route('/de_gym/de_gym/objects/<model("de_gym.de_gym"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_gym.object', {
#             'object': obj
#         })

