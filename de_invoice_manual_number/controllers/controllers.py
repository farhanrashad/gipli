# -*- coding: utf-8 -*-
# from odoo import http


# class DeInvoiceManualNumber(http.Controller):
#     @http.route('/de_invoice_manual_number/de_invoice_manual_number/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_invoice_manual_number/de_invoice_manual_number/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_invoice_manual_number.listing', {
#             'root': '/de_invoice_manual_number/de_invoice_manual_number',
#             'objects': http.request.env['de_invoice_manual_number.de_invoice_manual_number'].search([]),
#         })

#     @http.route('/de_invoice_manual_number/de_invoice_manual_number/objects/<model("de_invoice_manual_number.de_invoice_manual_number"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_invoice_manual_number.object', {
#             'object': obj
#         })
