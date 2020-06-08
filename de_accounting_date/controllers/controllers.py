# -*- coding: utf-8 -*-
# from odoo import http


# class DeAccountingDate(http.Controller):
#     @http.route('/de_accounting_date/de_accounting_date/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_accounting_date/de_accounting_date/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_accounting_date.listing', {
#             'root': '/de_accounting_date/de_accounting_date',
#             'objects': http.request.env['de_accounting_date.de_accounting_date'].search([]),
#         })

#     @http.route('/de_accounting_date/de_accounting_date/objects/<model("de_accounting_date.de_accounting_date"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_accounting_date.object', {
#             'object': obj
#         })
