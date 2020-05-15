# -*- coding: utf-8 -*-
# from odoo import http


# class DeAccountTaxRegiste(http.Controller):
#     @http.route('/de_account_tax_registe/de_account_tax_registe/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_account_tax_registe/de_account_tax_registe/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_account_tax_registe.listing', {
#             'root': '/de_account_tax_registe/de_account_tax_registe',
#             'objects': http.request.env['de_account_tax_registe.de_account_tax_registe'].search([]),
#         })

#     @http.route('/de_account_tax_registe/de_account_tax_registe/objects/<model("de_account_tax_registe.de_account_tax_registe"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_account_tax_registe.object', {
#             'object': obj
#         })
