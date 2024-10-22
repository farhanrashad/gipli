# -*- coding: utf-8 -*-
# from odoo import http


# class DePurchaseBudget(http.Controller):
#     @http.route('/de_purchase_budget/de_purchase_budget/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_purchase_budget/de_purchase_budget/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_purchase_budget.listing', {
#             'root': '/de_purchase_budget/de_purchase_budget',
#             'objects': http.request.env['de_purchase_budget.de_purchase_budget'].search([]),
#         })

#     @http.route('/de_purchase_budget/de_purchase_budget/objects/<model("de_purchase_budget.de_purchase_budget"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_purchase_budget.object', {
#             'object': obj
#         })
