# -*- coding: utf-8 -*-
# from odoo import http


# class DeSchoolStudent(http.Controller):
#     @http.route('/de_school_student/de_school_student', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_school_student/de_school_student/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_school_student.listing', {
#             'root': '/de_school_student/de_school_student',
#             'objects': http.request.env['de_school_student.de_school_student'].search([]),
#         })

#     @http.route('/de_school_student/de_school_student/objects/<model("de_school_student.de_school_student"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_school_student.object', {
#             'object': obj
#         })
