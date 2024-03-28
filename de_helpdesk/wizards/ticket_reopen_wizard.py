# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError

class TicketReopen(models.TransientModel):
    _name = 'project.ticket.reopen.wizard'
    _description = 'Ticket Reopen Wizard'

    ticket_ids = fields.Many2many(
        'project.task', default=lambda self: self.env.context.get('active_ids'))
    reopen_reason = fields.Text('Reason', required=True)
    stage_id = fields.Many2one('project.task.type', string='Reopen In', required=True,
        domain=lambda self: self._compute_stage_domain()
    )

    @api.model
    def _compute_stage_domain(self):
        # Compute the domain based on certain conditions
        domain = []
        if 'ticket_ids' in self.env.context:
            tickets = self.env['helpdesk.ticket'].browse(self.env.context['ticket_ids'])
            project_ids = tickets.mapped('project_id.id')
            domain = [('project_ids', 'in', project_ids)]
        return domain
        
    def action_reopen_tickets(self):
        reopen_reason_id = self.env['project.ticket.reopen']
        for ticket in self.ticket_ids:
            reopen_reason_id.create(ticket._prepare_ticket_reopen_reason_values(ticket,self.reopen_reason))
            ticket._prepare_ticket_reopen(ticket, stage_id)



