# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError

class TicketReopen(models.TransientModel):
    _name = 'project.ticket.reopen.wizard'
    _description = 'Ticket Reopen Wizard'

    ticket_ids = fields.Many2many(
        'project.task', default=lambda self: self.env.context.get('active_ids'))
    reopen_reason = fields.Text('Reason', required=True)
    
    #project_ids = fields.Many2many('project.project', string='Projects', compute='_compute_project_ids')

    #stage_id = fields.Many2one('project.task.type', string='Reopen In', required=True,
    #    domain="[('project_ids', 'in', project_ids),('fold', '=', False)]"
    #)

    @api.depends('ticket_ids')
    def _compute_project_ids(self):
        for record in self:
            record.project_ids = record.ticket_ids.mapped('project_id')


    #@api.depends('ticket_ids')
    def _compute_stage_domain(self):
        # Compute the domain based on certain conditions
        domain = []
        if 'ticket_ids' in self.env.context:
            tickets = self.env['helpdesk.ticket'].browse(self.env.context['ticket_ids'])
            project_ids = tickets.mapped('project_id')
            #raise UserError(project_ids)
            domain = [('project_ids', 'in', project_ids.ids)]
        return domain
        
    def action_reopen_tickets(self):
        reopen_reason_id = self.env['project.ticket.reopen']
        for ticket in self.ticket_ids:
            ticket.write(self._prepare_ticket_reopen_values(ticket.project_id))
            
            
    def _prepare_ticket_reopen_values(self, project_id):
        min_open_stage = self.env['project.task.type'].search([
                ('project_ids','in',project_id.id),
                ('active','=',True),
                ('fold','=',False),
        ], order='sequence', limit=1)
        if min_open_stage:
            min_stage_id = min_open_stage[0]
                
        return {
            'stage_id': min_stage_id.id,
            'reopen_reason': self.reopen_reason,
        }

