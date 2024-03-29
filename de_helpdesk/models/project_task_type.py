# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    prj_task_type_approval_line = fields.One2many('project.task.type.approvals', 'ticket_stage_id', string="Stage Approvals Line")

class ProjectTaskType(models.Model):
    _name = 'project.task.type.approvals'
    _description = 'Task Type Approvals'

    ticket_stage_id = fields.Many2one('project.task.type', string='Stage', required=True, ondelete='cascade', index=True)
    project_id = fields.Many2one('project.task', string='Ticket', required=True, ondelete='cascade', index=True)
    
    ticket_approval_type = fields.Char(string='Ticket Approval Type', compute='_compute_ticket_approval_type')

    group_ids = fields.Many2many('res.groups', 'project_ticket_stage_groups_rel',
        'ticket_type_id', 'group_id', string="Groups",
                              )
    user_ids = fields.Many2many('res.users', 'project_ticket_stage_users_rel',
        'ticket_type_id', 'user_id', string="users",
                              )
    
    group_ids = fields.Many2many('res.groups', string='Security Groups')

    def _compute_ticket_approval_type(self):
        for record in self:
            record.ticket_approval_type = record.project_id.ticket_approval_type

    