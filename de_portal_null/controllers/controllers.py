# -*- coding: utf-8 -*-
# from odoo import http


# class DePortalNull(http.Controller):
#     @http.route('/de_portal_null/de_portal_null', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_portal_null/de_portal_null/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_portal_null.listing', {
#             'root': '/de_portal_null/de_portal_null',
#             'objects': http.request.env['de_portal_null.de_portal_null'].search([]),
#         })

#     @http.route('/de_portal_null/de_portal_null/objects/<model("de_portal_null.de_portal_null"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_portal_null.object', {
#             'object': obj
#         })
