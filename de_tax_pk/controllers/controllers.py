# -*- coding: utf-8 -*-
# from odoo import http


# class DeTaxPk(http.Controller):
#     @http.route('/de_tax_pk/de_tax_pk', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_tax_pk/de_tax_pk/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_tax_pk.listing', {
#             'root': '/de_tax_pk/de_tax_pk',
#             'objects': http.request.env['de_tax_pk.de_tax_pk'].search([]),
#         })

#     @http.route('/de_tax_pk/de_tax_pk/objects/<model("de_tax_pk.de_tax_pk"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_tax_pk.object', {
#             'object': obj
#         })
