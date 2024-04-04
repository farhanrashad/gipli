# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProjectTicketType(models.Model):
    _name = 'project.ticket.type'
    _description = 'Ticket Type'

    name = fields.Char(string='Name', required=True)
    project_id = fields.Many2one('project.project', string="Helpdesk Team",
                                 domain="[('is_helpdesk_team', '=', True), ('active', '=', True)]"
                                )

    