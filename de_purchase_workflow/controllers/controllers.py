# -*- coding: utf-8 -*-
# from odoo import http


# class DeRequisitionWorkflow(http.Controller):
#     @http.route('/de_requisition_workflow/de_requisition_workflow/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_requisition_workflow/de_requisition_workflow/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_requisition_workflow.listing', {
#             'root': '/de_requisition_workflow/de_requisition_workflow',
#             'objects': http.request.env['de_requisition_workflow.de_requisition_workflow'].search([]),
#         })

#     @http.route('/de_requisition_workflow/de_requisition_workflow/objects/<model("de_requisition_workflow.de_requisition_workflow"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_requisition_workflow.object', {
#             'object': obj
#         })
