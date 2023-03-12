# -*- coding: utf-8 -*-
# from odoo import http


# class DeEmpShiftManagement(http.Controller):
#     @http.route('/de_emp_shift_management/de_emp_shift_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_emp_shift_management/de_emp_shift_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_emp_shift_management.listing', {
#             'root': '/de_emp_shift_management/de_emp_shift_management',
#             'objects': http.request.env['de_emp_shift_management.de_emp_shift_management'].search([]),
#         })

#     @http.route('/de_emp_shift_management/de_emp_shift_management/objects/<model("de_emp_shift_management.de_emp_shift_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_emp_shift_management.object', {
#             'object': obj
#         })
