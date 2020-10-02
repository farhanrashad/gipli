# -*- coding: utf-8 -*-
# from odoo import http


# class DeDiscountInvoices(http.Controller):
#     @http.route('/de_discount_invoices/de_discount_invoices/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_discount_invoices/de_discount_invoices/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_discount_invoices.listing', {
#             'root': '/de_discount_invoices/de_discount_invoices',
#             'objects': http.request.env['de_discount_invoices.de_discount_invoices'].search([]),
#         })

#     @http.route('/de_discount_invoices/de_discount_invoices/objects/<model("de_discount_invoices.de_discount_invoices"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_discount_invoices.object', {
#             'object': obj
#         })
