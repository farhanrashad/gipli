# -*- coding: utf-8 -*-
# from odoo import http


# class DeEmpBooksEosAccount(http.Controller):
#     @http.route('/de_emp_books_eos_account/de_emp_books_eos_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_emp_books_eos_account/de_emp_books_eos_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_emp_books_eos_account.listing', {
#             'root': '/de_emp_books_eos_account/de_emp_books_eos_account',
#             'objects': http.request.env['de_emp_books_eos_account.de_emp_books_eos_account'].search([]),
#         })

#     @http.route('/de_emp_books_eos_account/de_emp_books_eos_account/objects/<model("de_emp_books_eos_account.de_emp_books_eos_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_emp_books_eos_account.object', {
#             'object': obj
#         })
