# -*- coding: utf-8 -*-
# from odoo import http


# class DePayrollTaxes(http.Controller):
#     @http.route('/de_payroll_taxes/de_payroll_taxes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_payroll_taxes/de_payroll_taxes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_payroll_taxes.listing', {
#             'root': '/de_payroll_taxes/de_payroll_taxes',
#             'objects': http.request.env['de_payroll_taxes.de_payroll_taxes'].search([]),
#         })

#     @http.route('/de_payroll_taxes/de_payroll_taxes/objects/<model("de_payroll_taxes.de_payroll_taxes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_payroll_taxes.object', {
#             'object': obj
#         })
