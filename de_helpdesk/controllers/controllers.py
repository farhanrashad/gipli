# -*- coding: utf-8 -*-
# from odoo import http


# class DeHelpdesk(http.Controller):
#     @http.route('/de_helpdesk/de_helpdesk', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_helpdesk/de_helpdesk/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_helpdesk.listing', {
#             'root': '/de_helpdesk/de_helpdesk',
#             'objects': http.request.env['de_helpdesk.de_helpdesk'].search([]),
#         })

#     @http.route('/de_helpdesk/de_helpdesk/objects/<model("de_helpdesk.de_helpdesk"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_helpdesk.object', {
#             'object': obj
#         })

