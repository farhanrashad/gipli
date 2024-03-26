# -*- coding: utf-8 -*-
# from odoo import http


# class DeDiscordConnector(http.Controller):
#     @http.route('/de_discord_connector/de_discord_connector', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_discord_connector/de_discord_connector/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_discord_connector.listing', {
#             'root': '/de_discord_connector/de_discord_connector',
#             'objects': http.request.env['de_discord_connector.de_discord_connector'].search([]),
#         })

#     @http.route('/de_discord_connector/de_discord_connector/objects/<model("de_discord_connector.de_discord_connector"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_discord_connector.object', {
#             'object': obj
#         })

