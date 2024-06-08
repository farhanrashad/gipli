# -*- coding: utf-8 -*-
# from odoo import http


# class DeCrmKyb(http.Controller):
#     @http.route('/de_crm_kyb/de_crm_kyb', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_crm_kyb/de_crm_kyb/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_crm_kyb.listing', {
#             'root': '/de_crm_kyb/de_crm_kyb',
#             'objects': http.request.env['de_crm_kyb.de_crm_kyb'].search([]),
#         })

#     @http.route('/de_crm_kyb/de_crm_kyb/objects/<model("de_crm_kyb.de_crm_kyb"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_crm_kyb.object', {
#             'object': obj
#         })

