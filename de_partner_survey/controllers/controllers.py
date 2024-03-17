# -*- coding: utf-8 -*-
# from odoo import http


# class DePartnerSurvey(http.Controller):
#     @http.route('/de_partner_survey/de_partner_survey/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_partner_survey/de_partner_survey/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_partner_survey.listing', {
#             'root': '/de_partner_survey/de_partner_survey',
#             'objects': http.request.env['de_partner_survey.de_partner_survey'].search([]),
#         })

#     @http.route('/de_partner_survey/de_partner_survey/objects/<model("de_partner_survey.de_partner_survey"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_partner_survey.object', {
#             'object': obj
#         })
