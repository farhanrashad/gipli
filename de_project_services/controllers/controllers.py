# -*- coding: utf-8 -*-
# from odoo import http


# class DeProjectServices(http.Controller):
#     @http.route('/de_project_services/de_project_services', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_project_services/de_project_services/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_project_services.listing', {
#             'root': '/de_project_services/de_project_services',
#             'objects': http.request.env['de_project_services.de_project_services'].search([]),
#         })

#     @http.route('/de_project_services/de_project_services/objects/<model("de_project_services.de_project_services"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_project_services.object', {
#             'object': obj
#         })

