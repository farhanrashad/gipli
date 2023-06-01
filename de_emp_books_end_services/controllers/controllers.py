# -*- coding: utf-8 -*-
# from odoo import http


# class DeEmpBooksEndServices(http.Controller):
#     @http.route('/de_emp_books_end_services/de_emp_books_end_services/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_emp_books_end_services/de_emp_books_end_services/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_emp_books_end_services.listing', {
#             'root': '/de_emp_books_end_services/de_emp_books_end_services',
#             'objects': http.request.env['de_emp_books_end_services.de_emp_books_end_services'].search([]),
#         })

#     @http.route('/de_emp_books_end_services/de_emp_books_end_services/objects/<model("de_emp_books_end_services.de_emp_books_end_services"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_emp_books_end_services.object', {
#             'object': obj
#         })
