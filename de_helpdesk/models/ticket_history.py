# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProjectTicketHistory(models.Model):
    _name = 'project.ticket.log'
    _description = 'Tickets Log'

    ticket_id = fields.Many2one('project.task', string='Ticket', required=True)
    old_stage_id = fields.Many2one('project.task.type', string='Old Stage', required=True)
    new_stage_id = fields.Many2one('project.task.type', string='New Stage', required=True)
    