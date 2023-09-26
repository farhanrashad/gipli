# -*- coding: utf-8 -*-
# from odoo import http


# class DeHrWorkspaceTimesheet(http.Controller):
#     @http.route('/de_hr_workspace_timesheet/de_hr_workspace_timesheet', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_hr_workspace_timesheet/de_hr_workspace_timesheet/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_hr_workspace_timesheet.listing', {
#             'root': '/de_hr_workspace_timesheet/de_hr_workspace_timesheet',
#             'objects': http.request.env['de_hr_workspace_timesheet.de_hr_workspace_timesheet'].search([]),
#         })

#     @http.route('/de_hr_workspace_timesheet/de_hr_workspace_timesheet/objects/<model("de_hr_workspace_timesheet.de_hr_workspace_timesheet"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_hr_workspace_timesheet.object', {
#             'object': obj
#         })
