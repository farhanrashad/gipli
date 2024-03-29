# -*- coding: utf-8 -*-

from odoo import models, fields, api

TICKET_PRIORITY = [
    ('0', 'Low priority'),
    ('1', 'Medium priority'),
    ('2', 'High priority'),
    ('3', 'Urgent'),
]

class Project(models.Model):
    _inherit = 'project.project'

    auto_assignment = fields.Boolean("Automatic Assignment")
    assign_method = fields.Selection([
        ('randomly', 'Each user is assigned an equal number of tickets'),
        ('balanced', 'Each user has an equal number of open tickets')],
        string='Assignment Method', default='randomly',
        help="New tickets will automatically be assigned to the team members that are available, according to their working hours and their time off.")

    is_sla = fields.Boolean('SLA Policies', default=False)
    is_helpdesk_team = fields.Boolean('Helpdesk Team', default=False)

    group_merge_tickets = fields.Boolean('Merge Tickets', implied_group='de_helpdesk.group_project_ticket_merge')
    group_reopen_tickets = fields.Boolean('Reopen Tickets', implied_group='de_helpdesk.group_project_ticket_reopen')

    #is_ticket_approvals = fields.Boolean('Approvals', default=False)
    #is_ticket_approvals = fields.Boolean('Ticket Approvals', config_parameter='de_portal_hr_service.allow_portal_user')
    group_ticket_approvals = fields.Boolean(string="Ticket Approvals", 
                    implied_group='de_helpdesk.group_project_ticket_approvals')
    ticket_approval_type = fields.Selection([
        ('group', 'By Groups'),
        ('user', 'By Users')],
        string='Approval Type', default='group', 
        help="Select how approvals are granted: by security group or individual user."
    )
    
    close_ticket_count = fields.Integer(string='Ticket Closed', compute='_compute_close_ticket_count')
    open_ticket_count = fields.Integer(string='Ticket Closed', compute='_compute_open_ticket_count')
    unassigned_ticket_count = fields.Integer(string='Unassigned Tickets', compute='_compute_unassigned_tickets')
    urgent_ticket_count = fields.Integer(string='# Urgent Ticket', compute='_compute_urgent_ticket')
    sla_failed_ticket_count = fields.Integer(string='Failed SLA Ticket', compute='_compute_sla_failed')
    sla_success_rate = fields.Float(string='Success Rate', compute='_compute_sla_success_rate', groups="de_helpdesk.group_project_helpdesk_user")

    resource_calendar_id = fields.Many2one('resource.calendar', 'Working Hours',
        default=lambda self: self.env.company.resource_calendar_id, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Working hours used to determine the deadline of SLA Policies.")

    allow_submit_ticket_from_web = fields.Boolean('Website Form', readonly=False, store=True)


    allow_customer_rating = fields.Boolean('Customer Ratings')
    
    publish_rating = fields.Boolean('Publish Ratings')

    allow_portal_user_close_ticket = fields.Boolean('Closure by Customers')
    allow_portal_user_reopen_ticket = fields.Boolean('Re-open by Customers')
    allow_ticket_auto_close = fields.Boolean('Ticket Auto Clsoe')

    allow_stock_returns = fields.Boolean('Returns')
    
    from_stage_ids = fields.Many2many('project.task.type', 
        relation='project_ticket_stage_auto_close_from_rel',
        string='In Stages',
        domain="[('project_ids','in',id)]",
    )
    close_stage_id = fields.Many2one('project.task.type',
        string='Close to Stage',
        readonly=False, store=True,
        domain="[('project_ids','in',id)]",
    )
    day_to_close = fields.Integer('Inactive Period(days)',
        default=7,
        help="Period of inactivity after which tickets will be automatically closed.")


    # Compute Methods
    def _compute_close_ticket_count(self):
        for prj in self:
            prj.close_ticket_count = len(prj.task_ids.filtered(lambda x: x.stage_id.fold))
            
    def _compute_open_ticket_count(self):
        for prj in self:
            prj.open_ticket_count = len(prj.task_ids.filtered(lambda x: not x.stage_id.fold))

    def _compute_unassigned_tickets(self):
        for prj in self:
            prj.unassigned_ticket_count = len(prj.task_ids.filtered(lambda x: not x.user_ids))

    def _compute_urgent_ticket(self):
        for prj in self:
            prj.urgent_ticket_count = len(prj.task_ids.filtered(lambda x: not x.priority == 3))

    def _compute_sla_failed(self):
        for prj in self:
            prj.sla_failed_ticket_count = len(prj.task_ids.filtered(lambda x: not x.priority == 3))

    def _compute_sla_success_rate(self):
        for prj in self:
            prj.sla_success_rate = 33.45    
    # Actions
    def action_project_tickets(self):
        action = self.env.ref('de_helpdesk.action_project_helpdesk_all_task').read()[0]
        action.update({
            'name': 'Tickets',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'domain': [('project_id', '=', self.id)],
            'context': {
                'default_project_id': self.id,
                'search_default_my_ticket': 1,
            },
        })
        return action

    def action_project_closed_tickets(self):
        action = self.env.ref('de_helpdesk.action_project_helpdesk_all_task').read()[0]
        action.update({
            'name': 'Closed Tickets',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'domain': [('project_id', '=', self.id),('stage_id.fold', '=', True)],
            'context': {
                'default_project_id': self.id,
                'search_default_my_ticket': 1,
            },
        })
        return action

    def action_project_open_tickets(self):
        action = self.env.ref('de_helpdesk.action_project_helpdesk_all_task').read()[0]
        action.update({
            'name': 'Closed Tickets',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'domain': [('project_id', '=', self.id),('stage_id.fold', '=', False)],
            'context': {
                'default_project_id': self.id,
                'search_default_my_ticket': 1,
            },
        })
        return action

    def action_project_unassigned_tickets(self):
        action = self.env.ref('de_helpdesk.action_project_helpdesk_all_task').read()[0]
        action.update({
            'name': 'Unassigned Tickets',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'domain': [('project_id', '=', self.id),('user_ids', '=', False)],
            'context': {
                'default_project_id': self.id,
                'search_default_my_ticket': 1,
            },
        })
        return action

    def action_project_urgent_tickets(self):
        action = self.env.ref('de_helpdesk.action_project_helpdesk_all_task').read()[0]
        action.update({
            'name': 'Urgent Tickets',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'domain': [('project_id', '=', self.id),('priority', '=', 3)],
            'context': {
                'default_project_id': self.id,
                'search_default_my_ticket': 1,
            },
        })
        return action
        
    def action_view_tickets(self):
        pass

    def action_view_ticket_analysis(self):
        pass

    def action_view_sla_analysis(self):
        pass