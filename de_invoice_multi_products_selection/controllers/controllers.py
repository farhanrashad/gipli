# -*- coding: utf-8 -*-
# from odoo import http


# class DeInvoiceMultiProductsSelection(http.Controller):
#     @http.route('/de_invoice_multi_products_selection/de_invoice_multi_products_selection/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_invoice_multi_products_selection/de_invoice_multi_products_selection/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_invoice_multi_products_selection.listing', {
#             'root': '/de_invoice_multi_products_selection/de_invoice_multi_products_selection',
#             'objects': http.request.env['de_invoice_multi_products_selection.de_invoice_multi_products_selection'].search([]),
#         })

#     @http.route('/de_invoice_multi_products_selection/de_invoice_multi_products_selection/objects/<model("de_invoice_multi_products_selection.de_invoice_multi_products_selection"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_invoice_multi_products_selection.object', {
#             'object': obj
#         })
