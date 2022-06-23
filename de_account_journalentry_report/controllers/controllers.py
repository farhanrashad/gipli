# -*- coding: utf-8 -*-
# from odoo import http


# class DeAccountJournalentryReport(http.Controller):
#     @http.route('/de_account_journalentry_report/de_account_journalentry_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_account_journalentry_report/de_account_journalentry_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_account_journalentry_report.listing', {
#             'root': '/de_account_journalentry_report/de_account_journalentry_report',
#             'objects': http.request.env['de_account_journalentry_report.de_account_journalentry_report'].search([]),
#         })

#     @http.route('/de_account_journalentry_report/de_account_journalentry_report/objects/<model("de_account_journalentry_report.de_account_journalentry_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_account_journalentry_report.object', {
#             'object': obj
#         })
