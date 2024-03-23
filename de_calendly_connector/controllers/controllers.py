# -*- coding: utf-8 -*-
# from odoo import http


# class DeCalendlyConnector(http.Controller):
#     @http.route('/de_calendly_connector/de_calendly_connector', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_calendly_connector/de_calendly_connector/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_calendly_connector.listing', {
#             'root': '/de_calendly_connector/de_calendly_connector',
#             'objects': http.request.env['de_calendly_connector.de_calendly_connector'].search([]),
#         })

#     @http.route('/de_calendly_connector/de_calendly_connector/objects/<model("de_calendly_connector.de_calendly_connector"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_calendly_connector.object', {
#             'object': obj
#         })

