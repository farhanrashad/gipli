# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    prj_task_type_approval_line = fields.One2many('project.task.type.approvals', 'ticket_stage_id', 
                                                  string="Stage Approvals Line",
                                                 
                                                 )

    @api.onchange('project_ids')
    def _onchange_project_ids(self):
        # Clear existing approvals lines
        self.prj_task_type_approval_line.unlink()
        approval_lines = []
        for project_id in self.project_ids.filtered(lambda p: p.is_helpdesk_team):
            approval_lines.append((0, 0, {
                'ticket_stage_id': self.id,
                'project_id': project_id.id,
            }))
        
        self.prj_task_type_approval_line = approval_lines

class ProjectTaskType(models.Model):
    _name = 'project.task.type.approvals'
    _description = 'Task Type Approvals'

    ticket_stage_id = fields.Many2one('project.task.type', string='Stage', required=True, ondelete='cascade', index=True)
    project_id = fields.Many2one('project.project', string='Helpdesk Team', required=True, ondelete='cascade', index=True)
    
    group_approval = fields.Boolean(string='Group Approval', compute='_compute_all_approval_type')
    user_approval = fields.Boolean(string='Group Approval', compute='_compute_all_approval_type')

    group_ids = fields.Many2many('res.groups', 'project_ticket_stage_groups_rel',
        'ticket_type_id', 'group_id', string="Groups",
                              )
    user_ids = fields.Many2many('res.users', 'project_ticket_stage_users_rel',
        'ticket_type_id', 'user_id', string="Approvers",
                              )
    
    group_ids = fields.Many2many('res.groups', string='Security Groups')

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

    