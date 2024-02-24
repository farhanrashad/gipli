# -*- coding: utf-8 -*-
# from odoo import http


# class DeSocial(http.Controller):
#     @http.route('/de_social/de_social', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_social/de_social/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_social.listing', {
#             'root': '/de_social/de_social',
#             'objects': http.request.env['de_social.de_social'].search([]),
#         })

#     @http.route('/de_social/de_social/objects/<model("de_social.de_social"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_social.object', {
#             'object': obj
#         })

