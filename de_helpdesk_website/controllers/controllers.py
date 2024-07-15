# -*- coding: utf-8 -*-
# from odoo import http


# class DeHelpdeskWebsite(http.Controller):
#     @http.route('/de_helpdesk_website/de_helpdesk_website', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_helpdesk_website/de_helpdesk_website/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_helpdesk_website.listing', {
#             'root': '/de_helpdesk_website/de_helpdesk_website',
#             'objects': http.request.env['de_helpdesk_website.de_helpdesk_website'].search([]),
#         })

#     @http.route('/de_helpdesk_website/de_helpdesk_website/objects/<model("de_helpdesk_website.de_helpdesk_website"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_helpdesk_website.object', {
#             'object': obj
#         })

