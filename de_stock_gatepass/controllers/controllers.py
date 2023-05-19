# -*- coding: utf-8 -*-
# from odoo import http


# class DeStockGatepass(http.Controller):
#     @http.route('/de_stock_gatepass/de_stock_gatepass/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_stock_gatepass/de_stock_gatepass/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_stock_gatepass.listing', {
#             'root': '/de_stock_gatepass/de_stock_gatepass',
#             'objects': http.request.env['de_stock_gatepass.de_stock_gatepass'].search([]),
#         })

#     @http.route('/de_stock_gatepass/de_stock_gatepass/objects/<model("de_stock_gatepass.de_stock_gatepass"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_stock_gatepass.object', {
#             'object': obj
#         })
