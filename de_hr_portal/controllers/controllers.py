# -*- coding: utf-8 -*-
# from odoo import http


# class DeHrPortal(http.Controller):
#     @http.route('/de_hr_portal/de_hr_portal', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_hr_portal/de_hr_portal/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_hr_portal.listing', {
#             'root': '/de_hr_portal/de_hr_portal',
#             'objects': http.request.env['de_hr_portal.de_hr_portal'].search([]),
#         })

#     @http.route('/de_hr_portal/de_hr_portal/objects/<model("de_hr_portal.de_hr_portal"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_hr_portal.object', {
#             'object': obj
#         })

