# -*- coding: utf-8 -*-
# from odoo import http


# class DeReportBuilder(http.Controller):
#     @http.route('/de_report_builder/de_report_builder', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_report_builder/de_report_builder/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_report_builder.listing', {
#             'root': '/de_report_builder/de_report_builder',
#             'objects': http.request.env['de_report_builder.de_report_builder'].search([]),
#         })

#     @http.route('/de_report_builder/de_report_builder/objects/<model("de_report_builder.de_report_builder"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_report_builder.object', {
#             'object': obj
#         })

