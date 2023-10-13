# -*- coding: utf-8 -*-
# from odoo import http


# class DePaymentAllocation(http.Controller):
#     @http.route('/de_payment_allocation/de_payment_allocation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_payment_allocation/de_payment_allocation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_payment_allocation.listing', {
#             'root': '/de_payment_allocation/de_payment_allocation',
#             'objects': http.request.env['de_payment_allocation.de_payment_allocation'].search([]),
#         })

#     @http.route('/de_payment_allocation/de_payment_allocation/objects/<model("de_payment_allocation.de_payment_allocation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_payment_allocation.object', {
#             'object': obj
#         })
