# -*- coding: utf-8 -*-
# from odoo import http


# class DeLotSerial(http.Controller):
#     @http.route('/de_lot_serial/de_lot_serial/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_lot_serial/de_lot_serial/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_lot_serial.listing', {
#             'root': '/de_lot_serial/de_lot_serial',
#             'objects': http.request.env['de_lot_serial.de_lot_serial'].search([]),
#         })

#     @http.route('/de_lot_serial/de_lot_serial/objects/<model("de_lot_serial.de_lot_serial"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_lot_serial.object', {
#             'object': obj
#         })
