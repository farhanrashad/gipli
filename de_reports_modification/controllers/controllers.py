# -*- coding: utf-8 -*-
# from odoo import http


# class DeReportsModification(http.Controller):
#     @http.route('/de_reports_modification/de_reports_modification/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_reports_modification/de_reports_modification/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_reports_modification.listing', {
#             'root': '/de_reports_modification/de_reports_modification',
#             'objects': http.request.env['de_reports_modification.de_reports_modification'].search([]),
#         })

#     @http.route('/de_reports_modification/de_reports_modification/objects/<model("de_reports_modification.de_reports_modification"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_reports_modification.object', {
#             'object': obj
#         })
