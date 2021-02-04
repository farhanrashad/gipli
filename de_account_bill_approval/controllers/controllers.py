# -*- coding: utf-8 -*-
# from odoo import http


# class DeAccountBillApproval(http.Controller):
#     @http.route('/de_account_bill_approval/de_account_bill_approval/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_account_bill_approval/de_account_bill_approval/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_account_bill_approval.listing', {
#             'root': '/de_account_bill_approval/de_account_bill_approval',
#             'objects': http.request.env['de_account_bill_approval.de_account_bill_approval'].search([]),
#         })

#     @http.route('/de_account_bill_approval/de_account_bill_approval/objects/<model("de_account_bill_approval.de_account_bill_approval"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_account_bill_approval.object', {
#             'object': obj
#         })
