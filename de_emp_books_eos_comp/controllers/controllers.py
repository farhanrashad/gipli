# -*- coding: utf-8 -*-
# from odoo import http


# class DeEmpBooksEosComp(http.Controller):
#     @http.route('/de_emp_books_eos_comp/de_emp_books_eos_comp/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_emp_books_eos_comp/de_emp_books_eos_comp/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_emp_books_eos_comp.listing', {
#             'root': '/de_emp_books_eos_comp/de_emp_books_eos_comp',
#             'objects': http.request.env['de_emp_books_eos_comp.de_emp_books_eos_comp'].search([]),
#         })

#     @http.route('/de_emp_books_eos_comp/de_emp_books_eos_comp/objects/<model("de_emp_books_eos_comp.de_emp_books_eos_comp"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_emp_books_eos_comp.object', {
#             'object': obj
#         })
