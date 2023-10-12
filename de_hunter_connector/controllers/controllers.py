# -*- coding: utf-8 -*-
# from odoo import http


# class DeHunterConnector(http.Controller):
#     @http.route('/de_hunter_connector/de_hunter_connector', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_hunter_connector/de_hunter_connector/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_hunter_connector.listing', {
#             'root': '/de_hunter_connector/de_hunter_connector',
#             'objects': http.request.env['de_hunter_connector.de_hunter_connector'].search([]),
#         })

#     @http.route('/de_hunter_connector/de_hunter_connector/objects/<model("de_hunter_connector.de_hunter_connector"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_hunter_connector.object', {
#             'object': obj
#         })
