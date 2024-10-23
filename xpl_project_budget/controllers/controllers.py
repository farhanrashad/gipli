# -*- coding: utf-8 -*-
# from odoo import http


# class XplProjectBudget(http.Controller):
#     @http.route('/xpl_project_budget/xpl_project_budget', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/xpl_project_budget/xpl_project_budget/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('xpl_project_budget.listing', {
#             'root': '/xpl_project_budget/xpl_project_budget',
#             'objects': http.request.env['xpl_project_budget.xpl_project_budget'].search([]),
#         })

#     @http.route('/xpl_project_budget/xpl_project_budget/objects/<model("xpl_project_budget.xpl_project_budget"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('xpl_project_budget.object', {
#             'object': obj
#         })

