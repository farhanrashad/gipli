# -*- coding: utf-8 -*-
# from odoo import http


# class DePurchaseDynamicReport(http.Controller):
#     @http.route('/de_purchase_dynamic_report/de_purchase_dynamic_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_purchase_dynamic_report/de_purchase_dynamic_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_purchase_dynamic_report.listing', {
#             'root': '/de_purchase_dynamic_report/de_purchase_dynamic_report',
#             'objects': http.request.env['de_purchase_dynamic_report.de_purchase_dynamic_report'].search([]),
#         })

#     @http.route('/de_purchase_dynamic_report/de_purchase_dynamic_report/objects/<model("de_purchase_dynamic_report.de_purchase_dynamic_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_purchase_dynamic_report.object', {
#             'object': obj
#         })

