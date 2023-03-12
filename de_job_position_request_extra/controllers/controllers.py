# -*- coding: utf-8 -*-
# from odoo import http


# class DeJobPositionRequestExtra(http.Controller):
#     @http.route('/de_job_position_request_extra/de_job_position_request_extra/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_job_position_request_extra/de_job_position_request_extra/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_job_position_request_extra.listing', {
#             'root': '/de_job_position_request_extra/de_job_position_request_extra',
#             'objects': http.request.env['de_job_position_request_extra.de_job_position_request_extra'].search([]),
#         })

#     @http.route('/de_job_position_request_extra/de_job_position_request_extra/objects/<model("de_job_position_request_extra.de_job_position_request_extra"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_job_position_request_extra.object', {
#             'object': obj
#         })
