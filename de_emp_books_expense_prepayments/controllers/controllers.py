# -*- coding: utf-8 -*-
# from odoo import http


# class DeEmpfinExpenseAdvances(http.Controller):
#     @http.route('/de_empfin_expense_advances/de_empfin_expense_advances/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_empfin_expense_advances/de_empfin_expense_advances/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_empfin_expense_advances.listing', {
#             'root': '/de_empfin_expense_advances/de_empfin_expense_advances',
#             'objects': http.request.env['de_empfin_expense_advances.de_empfin_expense_advances'].search([]),
#         })

#     @http.route('/de_empfin_expense_advances/de_empfin_expense_advances/objects/<model("de_empfin_expense_advances.de_empfin_expense_advances"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_empfin_expense_advances.object', {
#             'object': obj
#         })
