# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError

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
        tickets_description = '\n'.join(ticket.description for ticket in self.ticket_ids.sorted(key=lambda t: t.create_date))
        tickets_name = ','.join(ticket.ticket_no for ticket in self.ticket_ids.sorted(key=lambda t: t.create_date))
        tickets_name = 'Combine tickets ' + tickets_name
        if self.merge_method == 'new':
            ticket = self._create_ticket(tickets_name, tickets_description)
        elif self.merge_method == 'one':
            ticket = self._merge_tickets(tickets_description)
            #raise UserError(to_combine_ticket_ids)
            #raise UserError(self.ticket_ids[0])
            

    def _create_ticket(self, name, description):
        ticket = self.env['project.task'].create(self._prepare_ticket_values(name, description))
        lang = ticket.partner_id.lang or self.env.user.lang
        message_body = ticket._get_ticket_merge_digest(ticket, lang=lang)
        self._send_message(self.ticket_ids, message_body)
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

    def _merge_tickets(self, description):
        ticket = self.ticket_ids[0]
        to_combine_ticket_ids = self.ticket_ids - ticket
        
        ticket.write(self._prepare_ticket_updated_values(description))
        
        lang = ticket.partner_id.lang or self.env.user.lang
        message_body = ticket._get_ticket_merge_digest(ticket, lang=lang)
        self._send_message(to_combine_ticket_ids, message_body)

    
    def _prepare_ticket_updated_values(self,description):
        vals = {
            'description': description,
        }
        return vals
        
    def _send_message(self, ticket_ids, message_body):
        for ticket_id in ticket_ids:
            ticket_id.message_post(body=message_body)
