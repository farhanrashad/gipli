# -*- coding: utf-8 -*-
# from odoo import http


# class DeSchoolSale(http.Controller):
#     @http.route('/de_school_sale/de_school_sale', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_school_sale/de_school_sale/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_school_sale.listing', {
#             'root': '/de_school_sale/de_school_sale',
#             'objects': http.request.env['de_school_sale.de_school_sale'].search([]),
#         })

#     @http.route('/de_school_sale/de_school_sale/objects/<model("de_school_sale.de_school_sale"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_school_sale.object', {
#             'object': obj
#         })
