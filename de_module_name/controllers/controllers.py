# -*- coding: utf-8 -*-
# from odoo import http


# class DeModuleName(http.Controller):
#     @http.route('/de_module_name/de_module_name/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_module_name/de_module_name/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_module_name.listing', {
#             'root': '/de_module_name/de_module_name',
#             'objects': http.request.env['de_module_name.de_module_name'].search([]),
#         })

#     @http.route('/de_module_name/de_module_name/objects/<model("de_module_name.de_module_name"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_module_name.object', {
#             'object': obj
#         })
