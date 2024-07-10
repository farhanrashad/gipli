# -*- coding: utf-8 -*-
# from odoo import http


# class HrCustomNeed(http.Controller):
#     @http.route('/hr_custom_need/hr_custom_need/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_custom_need/hr_custom_need/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_custom_need.listing', {
#             'root': '/hr_custom_need/hr_custom_need',
#             'objects': http.request.env['hr_custom_need.hr_custom_need'].search([]),
#         })

#     @http.route('/hr_custom_need/hr_custom_need/objects/<model("hr_custom_need.hr_custom_need"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_custom_need.object', {
#             'object': obj
#         })
