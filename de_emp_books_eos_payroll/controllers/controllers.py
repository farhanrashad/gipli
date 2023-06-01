# -*- coding: utf-8 -*-
# from odoo import http


# class DeEmpBooksEosPayroll(http.Controller):
#     @http.route('/de_emp_books_eos_payroll/de_emp_books_eos_payroll/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_emp_books_eos_payroll/de_emp_books_eos_payroll/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_emp_books_eos_payroll.listing', {
#             'root': '/de_emp_books_eos_payroll/de_emp_books_eos_payroll',
#             'objects': http.request.env['de_emp_books_eos_payroll.de_emp_books_eos_payroll'].search([]),
#         })

#     @http.route('/de_emp_books_eos_payroll/de_emp_books_eos_payroll/objects/<model("de_emp_books_eos_payroll.de_emp_books_eos_payroll"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_emp_books_eos_payroll.object', {
#             'object': obj
#         })
