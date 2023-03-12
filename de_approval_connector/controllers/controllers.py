# -*- coding: utf-8 -*-
# from odoo import http


# class DeApprovalConnector(http.Controller):
#     @http.route('/de_approval_connector/de_approval_connector/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_approval_connector/de_approval_connector/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_approval_connector.listing', {
#             'root': '/de_approval_connector/de_approval_connector',
#             'objects': http.request.env['de_approval_connector.de_approval_connector'].search([]),
#         })

#     @http.route('/de_approval_connector/de_approval_connector/objects/<model("de_approval_connector.de_approval_connector"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_approval_connector.object', {
#             'object': obj
#         })
