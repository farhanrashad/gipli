# -*- coding: utf-8 -*-
# from odoo import http


# class DeSaleCustomerStage(http.Controller):
#     @http.route('/de_sale_customer_stage/de_sale_customer_stage/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_sale_customer_stage/de_sale_customer_stage/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_sale_customer_stage.listing', {
#             'root': '/de_sale_customer_stage/de_sale_customer_stage',
#             'objects': http.request.env['de_sale_customer_stage.de_sale_customer_stage'].search([]),
#         })

#     @http.route('/de_sale_customer_stage/de_sale_customer_stage/objects/<model("de_sale_customer_stage.de_sale_customer_stage"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_sale_customer_stage.object', {
#             'object': obj
#         })
