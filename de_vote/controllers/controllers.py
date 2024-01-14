# -*- coding: utf-8 -*-
# from odoo import http


# class DeVote(http.Controller):
#     @http.route('/de_vote/de_vote', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_vote/de_vote/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_vote.listing', {
#             'root': '/de_vote/de_vote',
#             'objects': http.request.env['de_vote.de_vote'].search([]),
#         })

#     @http.route('/de_vote/de_vote/objects/<model("de_vote.de_vote"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_vote.object', {
#             'object': obj
#         })
