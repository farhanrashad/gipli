# -*- coding: utf-8 -*-
# from odoo import http


# class DeRetailPriceTotal(http.Controller):
#     @http.route('/de_retail_price_total/de_retail_price_total/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_retail_price_total/de_retail_price_total/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_retail_price_total.listing', {
#             'root': '/de_retail_price_total/de_retail_price_total',
#             'objects': http.request.env['de_retail_price_total.de_retail_price_total'].search([]),
#         })

#     @http.route('/de_retail_price_total/de_retail_price_total/objects/<model("de_retail_price_total.de_retail_price_total"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_retail_price_total.object', {
#             'object': obj
#         })
