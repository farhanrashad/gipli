# -*- coding: utf-8 -*-
# from odoo import http


# class DePaymentAutorun(http.Controller):
#     @http.route('/de_payment_autorun/de_payment_autorun', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_payment_autorun/de_payment_autorun/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_payment_autorun.listing', {
#             'root': '/de_payment_autorun/de_payment_autorun',
#             'objects': http.request.env['de_payment_autorun.de_payment_autorun'].search([]),
#         })

#     @http.route('/de_payment_autorun/de_payment_autorun/objects/<model("de_payment_autorun.de_payment_autorun"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_payment_autorun.object', {
#             'object': obj
#         })

