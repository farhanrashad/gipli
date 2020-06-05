# -*- coding: utf-8 -*-
# from odoo import http


# class DeAccountDefaultDate(http.Controller):
#     @http.route('/de_account_default_date/de_account_default_date/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_account_default_date/de_account_default_date/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_account_default_date.listing', {
#             'root': '/de_account_default_date/de_account_default_date',
#             'objects': http.request.env['de_account_default_date.de_account_default_date'].search([]),
#         })

#     @http.route('/de_account_default_date/de_account_default_date/objects/<model("de_account_default_date.de_account_default_date"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_account_default_date.object', {
#             'object': obj
#         })
