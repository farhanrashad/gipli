# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProjectTicketType(models.Model):
    _name = 'project.ticket.type'
    _description = 'Activity Type'

    name = fields.Char(string='Name', required=True)

    