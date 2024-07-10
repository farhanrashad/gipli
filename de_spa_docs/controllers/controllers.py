# -*- coding: utf-8 -*-
# from odoo import http


# class DeSpaDocs(http.Controller):
#     @http.route('/de_spa_docs/de_spa_docs', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_spa_docs/de_spa_docs/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_spa_docs.listing', {
#             'root': '/de_spa_docs/de_spa_docs',
#             'objects': http.request.env['de_spa_docs.de_spa_docs'].search([]),
#         })

#     @http.route('/de_spa_docs/de_spa_docs/objects/<model("de_spa_docs.de_spa_docs"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_spa_docs.object', {
#             'object': obj
#         })

