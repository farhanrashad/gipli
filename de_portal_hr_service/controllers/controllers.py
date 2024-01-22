# -*- coding: utf-8 -*-
# from odoo import http


# class DePortalHrService(http.Controller):
#     @http.route('/de_portal_hr_service/de_portal_hr_service', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_portal_hr_service/de_portal_hr_service/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_portal_hr_service.listing', {
#             'root': '/de_portal_hr_service/de_portal_hr_service',
#             'objects': http.request.env['de_portal_hr_service.de_portal_hr_service'].search([]),
#         })

#     @http.route('/de_portal_hr_service/de_portal_hr_service/objects/<model("de_portal_hr_service.de_portal_hr_service"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_portal_hr_service.object', {
#             'object': obj
#         })

