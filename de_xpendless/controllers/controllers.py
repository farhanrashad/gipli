# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class TicketCustomerPortal(CustomerPortal):
#     @http.route('/de_xpendless/de_xpendless', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_xpendless/de_xpendless/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_xpendless.listing', {
#             'root': '/de_xpendless/de_xpendless',
#             'objects': http.request.env['de_xpendless.de_xpendless'].search([]),
#         })

#     @http.route('/de_xpendless/de_xpendless/objects/<model("de_xpendless.de_xpendless"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_xpendless.object', {
#             'object': obj
#         })

