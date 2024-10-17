# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    ticket_stage_approval_ids = fields.One2many('project.ticket.stage.approvals', 'ticket_stage_id', 
                                                  string="Stage Approvals Line",
                                                 
                                                 )

    ticket_approvals = fields.Boolean(string='Ticket Approvals Feature', compute='_compute_ticket_approvals')

    def _compute_ticket_approvals(self):
        for record in self:
            projects = record.project_ids.filtered(lambda x:x.is_helpdesk_team)
            if projects and any(project.is_ticket_approvals for project in projects):
                record.ticket_approvals = True
            else:
                record.ticket_approvals = False
                
    @api.onchange('project_ids')
    def _onchange_project_ids(self):
        # Clear existing approvals lines
        self.ticket_stage_approval_ids.unlink()
        approval_lines = []
        for project_id in self.project_ids.filtered(lambda p: p.is_helpdesk_team):
            approval_lines.append((0, 0, {
                'ticket_stage_id': self.id,
                'project_id': project_id.id,
            }))
        
        self.ticket_stage_approval_ids = approval_lines

class ProjectTicketStageApprovals(models.Model):
    _name = 'project.ticket.stage.approvals'
    _description = 'Ticket Stage Approvals'

    ticket_stage_id = fields.Many2one('project.task.type', string='Stage', required=True, ondelete='cascade', index=True)
    project_id = fields.Many2one('project.project', string='Helpdesk Team', required=True, ondelete='cascade', index=True)
    
    ticket_approval_type = fields.Char(string='Ticket Approval Type', compute='_compute_ticket_approval_type')

    group_ids = fields.Many2many('res.groups', 'project_ticket_stage_groups_rel',
        'ticket_type_id', 'group_id', string="Groups",
                              )
    user_ids = fields.Many2many('res.users', 'project_ticket_stage_users_rel',
        'ticket_type_id', 'user_id', string="Approvers",
                              )
    
    group_ids = fields.Many2many('res.groups', string='Security Groups')

    def _compute_ticket_approval_type(self):
        for record in self:
            record.ticket_approval_type = record.project_id.ticket_approval_type
            
    def _compute_all_approval_type(self):
        for record in self:
            if record.project_id.ticket_approval_type == 'group':
                record.group_approval = True
                record.user_approval = False
            elif record.project_id.ticket_approval_type == 'group':
                record.user_approval = True
                record.group_approval = False
            else:
                record.user_approval = False
                record.group_approval = False

    