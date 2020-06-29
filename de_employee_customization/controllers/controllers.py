# -*- coding: utf-8 -*-
# from odoo import http


# class DeEmployeeCustomization(http.Controller):
#     @http.route('/de_employee_customization/de_employee_customization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_employee_customization/de_employee_customization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_employee_customization.listing', {
#             'root': '/de_employee_customization/de_employee_customization',
#             'objects': http.request.env['de_employee_customization.de_employee_customization'].search([]),
#         })

#     @http.route('/de_employee_customization/de_employee_customization/objects/<model("de_employee_customization.de_employee_customization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_employee_customization.object', {
#             'object': obj
#         })
