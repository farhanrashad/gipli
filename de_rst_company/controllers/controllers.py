# -*- coding: utf-8 -*-
# from odoo import http


# class DeRstCompany(http.Controller):
#     @http.route('/de_rst_company/de_rst_company/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_rst_company/de_rst_company/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_rst_company.listing', {
#             'root': '/de_rst_company/de_rst_company',
#             'objects': http.request.env['de_rst_company.de_rst_company'].search([]),
#         })

#     @http.route('/de_rst_company/de_rst_company/objects/<model("de_rst_company.de_rst_company"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_rst_company.object', {
#             'object': obj
#         })
