# -*- coding: utf-8 -*-
# from odoo import http


# class DeSubscription(http.Controller):
#     @http.route('/de_subscription/de_subscription', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_subscription/de_subscription/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_subscription.listing', {
#             'root': '/de_subscription/de_subscription',
#             'objects': http.request.env['de_subscription.de_subscription'].search([]),
#         })

#     @http.route('/de_subscription/de_subscription/objects/<model("de_subscription.de_subscription"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_subscription.object', {
#             'object': obj
#         })

