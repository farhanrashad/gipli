# -*- coding: utf-8 -*-
# from odoo import http


# class DeHrShift(http.Controller):
#     @http.route('/de_hr_shift/de_hr_shift', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_hr_shift/de_hr_shift/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_hr_shift.listing', {
#             'root': '/de_hr_shift/de_hr_shift',
#             'objects': http.request.env['de_hr_shift.de_hr_shift'].search([]),
#         })

#     @http.route('/de_hr_shift/de_hr_shift/objects/<model("de_hr_shift.de_hr_shift"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_hr_shift.object', {
#             'object': obj
#         })
