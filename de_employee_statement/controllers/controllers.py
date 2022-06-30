# -*- coding: utf-8 -*-
# from odoo import http


# class DeEmployeeStatement(http.Controller):
#     @http.route('/de_employee_statement/de_employee_statement/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_employee_statement/de_employee_statement/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_employee_statement.listing', {
#             'root': '/de_employee_statement/de_employee_statement',
#             'objects': http.request.env['de_employee_statement.de_employee_statement'].search([]),
#         })

#     @http.route('/de_employee_statement/de_employee_statement/objects/<model("de_employee_statement.de_employee_statement"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_employee_statement.object', {
#             'object': obj
#         })
