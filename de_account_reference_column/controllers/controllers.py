# -*- coding: utf-8 -*-
# from odoo import http


# class DeAccountReferenceColumn(http.Controller):
#     @http.route('/de_account_reference_column/de_account_reference_column/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_account_reference_column/de_account_reference_column/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_account_reference_column.listing', {
#             'root': '/de_account_reference_column/de_account_reference_column',
#             'objects': http.request.env['de_account_reference_column.de_account_reference_column'].search([]),
#         })

#     @http.route('/de_account_reference_column/de_account_reference_column/objects/<model("de_account_reference_column.de_account_reference_column"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_account_reference_column.object', {
#             'object': obj
#         })
