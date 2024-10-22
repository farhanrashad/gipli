# -*- coding: utf-8 -*-
# from odoo import http


# class DeProjectRequisitionApprovals(http.Controller):
#     @http.route('/de_project_requisition_approvals/de_project_requisition_approvals', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_project_requisition_approvals/de_project_requisition_approvals/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_project_requisition_approvals.listing', {
#             'root': '/de_project_requisition_approvals/de_project_requisition_approvals',
#             'objects': http.request.env['de_project_requisition_approvals.de_project_requisition_approvals'].search([]),
#         })

#     @http.route('/de_project_requisition_approvals/de_project_requisition_approvals/objects/<model("de_project_requisition_approvals.de_project_requisition_approvals"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_project_requisition_approvals.object', {
#             'object': obj
#         })

