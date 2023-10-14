# -*- coding: utf-8 -*-
# from odoo import http


# class DeVoteCore(http.Controller):
#     @http.route('/de_vote_core/de_vote_core', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_vote_core/de_vote_core/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_vote_core.listing', {
#             'root': '/de_vote_core/de_vote_core',
#             'objects': http.request.env['de_vote_core.de_vote_core'].search([]),
#         })

#     @http.route('/de_vote_core/de_vote_core/objects/<model("de_vote_core.de_vote_core"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_vote_core.object', {
#             'object': obj
#         })
