# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProjectTicketReopen(models.Model):
    _name = 'project.ticket.reopen'
    _description = 'Re-open Ticket'

    name = fields.Text(string='Reason', required=True)
    ticket_id = fields.Many2one('project.task', 'Ticket')
    date_reopen = fields.Datetime("Reopen at", required=True)
    reopen_by = fields.Selection([
        ('customer', 'Closed by Customer'), 
        ('user', 'Closed by User')],
        string='Re-Open By',
    )