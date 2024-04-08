# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
from bs4 import BeautifulSoup

class TicketMergeWizard(models.TransientModel):
    _name = 'project.ticket.merge.wizard'
    _description = 'Ticket Reopen Wizard'
 
    ticket_ids = fields.Many2many(
        'project.task', default=lambda self: self.env.context.get('active_ids'))
    
    project_id = fields.Many2one('project.project', string='Helpdesk Team', 
                                  compute='_compute_project_id',
                                 domain="[('is_helpdesk_team','=',True)]",
                                  store=True, readonly=False, required=True
                                 )

    user_ids = fields.Many2many('res.users',string='Assignee')
    merge_method = fields.Selection([
        ('new', 'Merge in a new ticket'), 
        ('one', 'Merge in one ticket'), 
        ('ticket', 'Merge in a selected ticket')],
        string='Merge By', required=True, default='new'
    )
    target_ticket_id = fields.Many2one('project.task', string='Ticket',
                                       domain="[('id','in',ticket_ids)]"
                                      )
    
    @api.depends('ticket_ids.project_id')
    def _compute_project_id(self):
        for ticket in self:
            projects = ticket.ticket_ids.mapped('project_id')
            if len(projects) == 1:
                ticket.project_id = projects.id
            else:
                ticket.project_id = False

        
    def action_merge_tickets(self):
        if self.merge_method == 'new':
            ticket = self._create_ticket()
        elif self.merge_method == 'one':
            ticket = self._merge_tickets(self.ticket_ids[0])
        elif self.merge_method == 'ticket':
            ticket = self._merge_tickets(self.target_ticket_id)

    def _create_ticket(self):
        description = '\n'.join(str(ticket.description) for ticket in self.ticket_ids.sorted(key=lambda t: t.create_date))
        name = ','.join(ticket.ticket_no for ticket in self.ticket_ids.sorted(key=lambda t: t.create_date))
        name = 'Combine tickets ' + name
        ticket = self.env['project.task'].create(self._prepare_ticket_values(name, description))
        lang = ticket.partner_id.lang or self.env.user.lang
        message_body = ticket._get_ticket_merge_digest(ticket, lang=lang)
        self._send_message(self.ticket_ids, message_body)
        for ticket in self.ticket_ids:
            self._close_tickets(ticket)
        return ticket
        
    def _prepare_ticket_values(self, name, description):
        partner_id = self.ticket_ids.filtered(lambda x:x.partner_id).mapped('partner_id')
        vals = {
            'name': name,
            'project_id': self.project_id.id,
            'user_ids': self.user_ids.ids,
            'description': description,
            'is_ticket': True,
        }
        if partner_id:
            vals['partner_id'] = partner_id.id
        return vals

    def _merge_tickets(self, ticket_id):
        ticket = ticket_id
        to_combine_ticket_ids = self.ticket_ids - ticket
        # Convert ticket description to string using prettify()
        ticket_description_str = BeautifulSoup(ticket.description, 'html.parser').prettify()
        # Convert descriptions of to_combine_ticket_ids to strings
        descriptions = []
        for t in to_combine_ticket_ids.sorted(key=lambda t: t.create_date):
            descriptions.append(BeautifulSoup(t.description, 'html.parser').prettify())
        # Join descriptions with newlines
        tickets_description = '\n'.join(descriptions)
        # Combine descriptions
        description = ticket_description_str + '\n' + tickets_description
        ticket.sudo().update(self._prepare_ticket_updated_values(description))
        lang = ticket.partner_id.lang or self.env.user.lang
        message_body = ticket._get_ticket_merge_digest(ticket, lang=lang)
        self._send_message(to_combine_ticket_ids, message_body)
        for ticket in to_combine_ticket_ids:
            self._close_tickets(ticket)
    
    def _prepare_ticket_updated_values(self,description):
        partner_id = self.ticket_ids.filtered(lambda x:x.partner_id).mapped('partner_id')
        vals = {
            'description': BeautifulSoup(description, 'html.parser').prettify(),
            'partner_id': partner_id.id,
        }
        if self.user_ids:
            vals['user_ids'] = self.user_ids.ids
        return vals
        
    def _send_message(self, ticket_ids, message_body):
        for ticket_id in ticket_ids:
            ticket_id.message_post(body=message_body,message_type='comment')

    def _close_tickets(self, ticket_id):
        #close_stage_id = self.env['project.task.type']
        close_stage_id = self.env['project.task.type'].search([
            ('project_ids','in',ticket_id.project_id.id),
            ('fold','=',True),
        ],limit=1)
        ticket_id.write({
            'stage_id': close_stage_id.id,
            'closed_by': 'user',
        })
