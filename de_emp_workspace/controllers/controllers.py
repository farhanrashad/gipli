# -*- coding: utf-8 -*-
# from odoo import http


# class DeEmpWorkspace(http.Controller):
#     @http.route('/de_emp_workspace/de_emp_workspace', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_emp_workspace/de_emp_workspace/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_emp_workspace.listing', {
#             'root': '/de_emp_workspace/de_emp_workspace',
#             'objects': http.request.env['de_emp_workspace.de_emp_workspace'].search([]),
#         })

#     @http.route('/de_emp_workspace/de_emp_workspace/objects/<model("de_emp_workspace.de_emp_workspace"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_emp_workspace.object', {
#             'object': obj
#         })
