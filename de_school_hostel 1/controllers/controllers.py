# -*- coding: utf-8 -*-
# from odoo import http


# class DeSchoolHostel(http.Controller):
#     @http.route('/de_school_hostel/de_school_hostel', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_school_hostel/de_school_hostel/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_school_hostel.listing', {
#             'root': '/de_school_hostel/de_school_hostel',
#             'objects': http.request.env['de_school_hostel.de_school_hostel'].search([]),
#         })

#     @http.route('/de_school_hostel/de_school_hostel/objects/<model("de_school_hostel.de_school_hostel"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_school_hostel.object', {
#             'object': obj
#         })

