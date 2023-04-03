# -*- coding: utf-8 -*-
# from odoo import http


# class DeRequisitionConstraints(http.Controller):
#     @http.route('/de_requisition_constraints/de_requisition_constraints/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_requisition_constraints/de_requisition_constraints/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_requisition_constraints.listing', {
#             'root': '/de_requisition_constraints/de_requisition_constraints',
#             'objects': http.request.env['de_requisition_constraints.de_requisition_constraints'].search([]),
#         })

#     @http.route('/de_requisition_constraints/de_requisition_constraints/objects/<model("de_requisition_constraints.de_requisition_constraints"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_requisition_constraints.object', {
#             'object': obj
#         })
