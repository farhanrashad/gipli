# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError

class TicketMergeWizard(models.TransientModel):
    _name = 'project.ticket.merge.wizard'
    _description = 'Ticket Reopen Wizard'

    ticket_ids = fields.Many2many(
        'project.task', default=lambda self: self.env.context.get('active_ids'))
    reopen_reason = fields.Text('Reason', required=True)
    
    project_ids = fields.Many2many('project.project', string='Projects', compute='_compute_project_ids')

    stage_id = fields.Many2one('project.task.type', string='Reopen In', required=True,
        domain="[('project_ids', 'in', project_ids),('fold', '=', False)]"
    )

    @api.depends('ticket_ids')
    def _compute_project_ids(self):
        for record in self:
            record.project_ids = record.ticket_ids.mapped('project_id')


    @api.depends('ticket_ids')
    def _compute_stage_domain(self):
        # Compute the domain based on certain conditions
        domain = []
        if 'ticket_ids' in self.env.context:
            tickets = self.env['helpdesk.ticket'].browse(self.env.context['ticket_ids'])
            project_ids = tickets.mapped('project_id')
            raise UserError(project_ids)
            domain = [('project_ids', 'in', project_ids.ids)]
        return domain
        
    def action_reopen_tickets(self):
        reopen_reason_id = self.env['project.ticket.reopen']
        for ticket in self.ticket_ids:
            reopen_reason_id.create(ticket._prepare_ticket_reopen_reason_values(ticket,self.reopen_reason))
            ticket._prepare_ticket_reopen(self.stage_id)
            ticket._get_ticket_reopen_digest(origin='user', lang=lang)



