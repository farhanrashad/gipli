# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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
        ('random', 'Each user is assigned an equal number of tickets'),
        ('equal', 'Each user has an equal number of open tickets')],
        string='Assignment Method', default='random',
        help="New tickets will automatically be assigned to the team members that are available, according to their working hours and their time off.")

    team_member_ids = fields.Many2many('res.users', string='Team Members', domain=lambda self: [('groups_id', 'in', self.env.ref('de_helpdesk.group_project_helpdesk_user').id)],
        default=lambda self: self.env.user, required=True)
    

    is_sla = fields.Boolean('SLA Policies', default=False)
    is_helpdesk_team = fields.Boolean('Helpdesk Team', default=False)

    is_merge_tickets = fields.Boolean('Merge Tickets', default=False)
    is_reopen_tickets = fields.Boolean('Reopen Tickets', default=False)
    is_ticket_approvals = fields.Boolean(string="Ticket Approvals", default=False)
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

    allow_portal_user_close_ticket = fields.Boolean('Close by Customers')
    allow_portal_user_reopen_ticket = fields.Boolean('Reopen by Customers')
    

    allow_stock_returns = fields.Boolean('Returns')

    allow_ticket_auto_close = fields.Boolean('Ticket Auto Clsoe')
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

    # smart buttons
    count_sla = fields.Integer('SLA', compute='_compute_sla_count')
    count_tickets_rating = fields.Integer('Rating', compute='_compute_customer_rating_count')
    tickets_avg_rating = fields.Float('Rating Avg.', compute='_compute_tickets_avg_rating')

    # Compute Methods
    def _compute_tickets_avg_rating(self):
        for record in self:
            ticket_ids = record.task_ids.filtered(lambda x: x.customer_rating)
            rating_scores = ticket_ids.mapped('rating_score')
            try:
                record.tickets_avg_rating = sum(rating_scores) / len(rating_scores)
            except ZeroDivisionError:
                record.tickets_avg_rating = 0  # or any default value

            
    def _compute_sla_count(self):
        sla_lines = self.env['project.ticket.sla.line']
        for record in self:
            sla_lines = self.env['project.ticket.sla.line'].search([('ticket_id','in',record.task_ids.ids)])
            record.count_sla = len(sla_lines)

    def _compute_customer_rating_count(self):
        for record in self:
            ticket_ids = record.task_ids.filtered(lambda x:x.customer_rating)
            record.count_tickets_rating = len(ticket_ids.mapped('rating_score'))
            
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
    
    # ----------------------------------------------------------------
    # --------------------------- CRUD Operations --------------------
    # ----------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        projects = super(Project, self).create(vals_list)
        projects.sudo()._compute_group_project_sla()
        return projects

    def write(self, vals):
        res = super(Project, self).write(vals)
        if 'is_sla' in vals:
            self.sudo()._compute_group_project_sla()
        if 'is_ticket_approvals' in vals:
            self.sudo()._handle_ticket_approvals()
        return res

    # Schedule Action
    @api.model
    def _cron_ticket_auto_close(self):
        today = fields.Date.today()
        inactive_period = timedelta(days=self.day_to_close)

        tickets_to_close = self.search([
            ('active', '=', True),
            ('project_id.allow_ticket_auto_close', '=', True),
            ('from_stage_ids', 'in', self.stage_id.id),
            ('date_last_stage_update', '<=', today - inactive_period),
        ])

        for ticket in tickets_to_close:
            ticket.stage_id = self.close_stage_id.id
        return True
        
    # SLA Policies
    def _check_group_project_sla_enabled(self, check_user_has_group=False):
        user_has_group_sla_enabled = self.user_has_groups('de_helpdesk.group_project_sla_enabled') if check_user_has_group else True
        return user_has_group_sla_enabled and self.env['project.project'].search([('is_sla', '=', True)], limit=1)
        
    def _get_group_project_helpdesk_user(self):
        return self.env.ref('de_helpdesk.group_project_helpdesk_user')

    def _get_group_project_sla_enabled(self):
        return self.env.ref('de_helpdesk.group_project_sla_enabled')
        
    def _compute_group_project_sla(self):
        sla_projects = self.filtered('is_sla')
        non_sla_projects = self - sla_projects
        group_sla_enabled = group_helpdesk_user = None
        user_has_group_sla_enabled = self.env.user.has_group('de_helpdesk.group_project_sla_enabled')

        if sla_projects:
            if not user_has_group_sla_enabled:
                group_sla_enabled = self._get_group_project_sla_enabled()
                group_helpdesk_user = self._get_group_project_helpdesk_user()
                group_helpdesk_user.write({
                    'implied_ids': [Command.link(group_sla_enabled.id)]
                })
            self.env['project.sla'].search([
                ('project_id', 'in', sla_projects.ids), ('active', '=', False),
            ]).write({'active': True})

        if non_sla_projects:
            self.env['project.sla'].search([('project_id', 'in', non_sla_projects.ids)]).write({'active': False})
            if user_has_group_sla_enabled and not self._check_group_project_sla_enabled():
                group_sla_enabled = group_sla_enabled or self._get_group_project_sla_enabled()
                group_helpdesk_user = group_helpdesk_user or self._get_group_project_helpdesk_user()
                group_helpdesk_user.write({
                    'implied_ids': [Command.unlink(group_sla_enabled.id)]
                })
                group_sla_enabled.write({'users': [(5, 0, 0)]})

    # Handle Ticket Approvals
    def _remove_approvals(self, project):
        approvals = self.env['project.ticket.stage.approvals'].search([
            ('project_id', '=', project.id),
        ])
        approvals.write({
            'user_ids': [(5, 0, 0)],  # Clear existing user_ids
            'group_ids': [(5, 0, 0)],  # Clear existing group_ids
        })
        
    def _handle_ticket_approvals(self):
        if not self.is_ticket_approvals:
            self._remove_approvals(self)
        
    # Merge Tickets
    def _check_merge_tickets_feature(self, check_user_has_group=False):
        user_has_group_sla_enabled = self.user_has_groups('de_helpdesk.group_project_merge_ticket_enabled') if check_user_has_group else True
        return user_has_group_sla_enabled and self.env['project.project'].search([('is_merge_tickets', '=', True)], limit=1)
        
    def _get_group_project_merge_ticket_enabled(self):
        return self.env.ref('de_helpdesk.group_project_merge_ticket_enabled')
        
    def _compute_group_project_merge_ticket(self):
        merge_tickets_projects = self.filtered('is_merge_tickets')
        non_mergeable_projects = self - merge_tickets_projects
        
        group_merge_tickets_enabled = group_helpdesk_user = None
        user_has_group_merge_ticket_enabled = self.env.user.has_group('de_helpdesk.group_project_merge_ticket_enabled')

        if merge_tickets_projects:
            if not user_has_group_merge_ticket_enabled:
                group_merge_tickets_enabled = self._get_group_project_merge_ticket_enabled()
                group_helpdesk_user = self._get_group_project_helpdesk_user()
                group_helpdesk_user.write({
                    'implied_ids': [Command.link(group_merge_tickets_enabled.id)]
                })   
        if non_mergeable_projects:
            #self.env['project.sla'].search([('project_id', 'in', non_sla_projects.ids)]).write({'active': False})
            if user_has_group_sla_enabled and not self._check_merge_tickets_feature():
                group_merge_tickets_enabled = group_sla_enabled or self._get_group_project_merge_ticket_enabled()
                group_helpdesk_user = group_helpdesk_user or self._get_group_project_helpdesk_user()
                group_helpdesk_user.write({
                    'implied_ids': [Command.unlink(group_merge_tickets_enabled.id)]
                })
                group_merge_tickets_enabled.write({'users': [(5, 0, 0)]})
        
    # Actions
    def action_open_tickets_view(self):
        action = self.env.ref('de_helpdesk.action_project_helpdesk_all_ticket').read()[0]
        action.update({
            'name': 'Tickets',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'domain': [('project_id', '=', self.id)],
        })
        return action

    def action_open_tickets_rating_view(self):
        action = self.env.ref('de_helpdesk.action_ticket_customer_rating').read()[0]
        ticket_ids = self.task_ids.filtered(lambda x:x.customer_rating)
        action.update({
            'name': 'Customer Rating',
            'view_mode': 'tree',
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', ticket_ids.ids)],
            'context': {
                'create':False,
                'edit': False,
                'delete': False,
            }
        })
        return action

    def action_open_tickets_sla_view(self):
        action = self.env.ref('de_helpdesk.action_task_ticket_line').read()[0]
        action.update({
            'name': 'SLA',
            'view_mode': 'tree',
            'res_model': 'project.ticket.sla.line',
            'type': 'ir.actions.act_window',
            'domain': [('ticket_id', 'in', self.task_ids.ids)],
            'context': {
                'create': False,
                'edit': False,
                'delete': False,
            }
        })
        return action

    
    def action_project_tickets(self):
        action = self.env.ref('de_helpdesk.action_project_helpdesk_all_ticket').read()[0]
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
        action = self.env.ref('de_helpdesk.action_project_helpdesk_all_ticket').read()[0]
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
        action = self.env.ref('de_helpdesk.action_project_helpdesk_all_ticket').read()[0]
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
        action = self.env.ref('de_helpdesk.action_project_helpdesk_all_ticket').read()[0]
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
        action = self.env.ref('de_helpdesk.action_project_helpdesk_all_ticket').read()[0]
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

    # JS Dashbaord
    @api.model
    def retrieve_dashboard(self):
        """ This function returns the values to populate the custom dashboard in
            the purchase order views.
        """
        self.check_access_rights('read')

        result = {
            'all_quotation': 0,
            'count_my_tickets': 0,
            'count_my_high_tickets':0,
            'count_my_urgent_tickets':0,
            
            'target_ticket_closed': 0,
            'target_ticket_rating': 0,
            'target_ticket_success': 0,

            'avg_open_hours': 0,
            'avg_open_hours_high': 0,
            'avg_open_hours_urgent': 0,

            'count_sla_failed': 0,
            'count_sla_failed_high': 0,
            'count_sla_failed_urgent': 0,

            'today_closed_tickets': 0,
            'today_closed_sla_success': 0,
            'today_closed_rating': 0,
            
            'closed_last_7days': 0,
            'closed_success_last_7days': 0,
            'closed_rating_last_7days': 0,
        }

        
        # easy counts
        so = self.env['project.project']
        
        ticket_ids = self.env['project.task']
        domain = [('is_ticket','=',True),('user_ids','in',self.env.user.id)]
        
        result['all_quotation'] = so.search_count([])

        # Open Tickets
        result['count_my_tickets'] = ticket_ids.search_count(domain)
        result['count_my_high_tickets'] = ticket_ids.search_count(domain+[('ticket_priority','=',2)])
        result['count_my_urgent_tickets'] = ticket_ids.search_count(domain+[('ticket_priority','=',3)])
        
        # Failed Tickets
        result['count_sla_failed'] = ticket_ids.search_count(domain+[('is_sla_fail','=',True)])
        result['count_sla_failed_high'] = ticket_ids.search_count(domain+[('ticket_priority','=',2),('is_sla_fail','=',True)])
        result['count_sla_failed_urgent'] = ticket_ids.search_count(domain+[('ticket_priority','=',3),('is_sla_fail','=',True)])

        # Average Open Hours
        query1 = """
            SELECT
                round(AVG(open_ticket_hours),2) AS avg_open_hours,
                round(AVG(CASE WHEN priority = '2' THEN open_ticket_hours ELSE 0 END),2) AS avg_open_hours_high,
                round(AVG(CASE WHEN priority = '3' THEN open_ticket_hours ELSE 0 END),2) AS avg_open_hours_urgent
            FROM report_project_ticket_analysis
        """
        query = """
            select round(AVG(a.open_ticket_hours),2) AS avg_open_hours,
                round(AVG(CASE WHEN a.priority = '2' THEN a.open_ticket_hours ELSE 0 END),2) AS avg_open_hours_high,
                round(AVG(CASE WHEN a.priority = '3' THEN a.open_ticket_hours ELSE 0 END),2) AS avg_open_hours_urgent
            from (
            SELECT
                EXTRACT(EPOCH FROM (COALESCE(t.date_closed, NOW() AT TIME ZONE 'UTC') - t.create_date)) / 3600 as open_ticket_hours,
                t.ticket_priority as priority
            FROM project_task t
            where t.is_ticket = True
            ) a
        """
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()
        for record in results:
            result['avg_open_hours'] = record['avg_open_hours'] if result else 0.0
            result['avg_open_hours_high'] = record['avg_open_hours_high'] if result else 0.0
            result['avg_open_hours_urgent'] = record['avg_open_hours_urgent'] if result else 0.0
        #else:
        #    result['avg_open_hours'] = 0
        #    result['avg_open_hours_high'] = 0
        #    result['avg_open_hours_urgent'] = 0

        #report_ticket_ids = self.env['report.project.ticket.analysis'].search([
        #    ('user_id','=',self.env.user.id),
        #    ('stage_id.fold', '!=', True)
        #])
        #if len(report_ticket_ids) > 0:
        #    result['avg_open_hours'] = round(sum(report_ticket_ids.mapped('open_ticket_hours')) / len(report_ticket_ids),2)
        #    result['avg_open_hours_high'] = round(sum(report_ticket_ids.filtered(lambda x:x.priority == '2').mapped('open_ticket_hours')) / len(report_ticket_ids),2)
        #    result['avg_open_hours_urgent'] = round(sum(report_ticket_ids.filtered(lambda x:x.priority == '3').mapped('open_ticket_hours')) / len(report_ticket_ids),2)
        #else:
        #    result['avg_open_hours'] = 0
        #    result['avg_open_hours_high'] = 0
        #    result['avg_open_hours_urgent'] = 0
        
        # Today closed
        today_date = datetime.now().date()
        today_start = datetime.combine(today_date, datetime.min.time())
        today_end = datetime.combine(today_date, datetime.max.time())
        today_closed_ticket_ids = ticket_ids.search(domain + [('date_closed', '>=', today_start), ('date_closed', '<=', today_end)])

        result['today_closed_tickets'] = len(today_closed_ticket_ids)
        if len(today_closed_ticket_ids) > 0:
            result['today_closed_sla_success'] = len(today_closed_ticket_ids.filtered(lambda x:x.is_sla_success)) / len(today_closed_ticket_ids)
            result['today_closed_rating'] = sum(today_closed_ticket_ids.mapped('rating_score')) / len(today_closed_ticket_ids)
        else:
            result['today_closed_sla_success'] = 0
            result['today_closed_rating'] = 0
            
        # Last 7 Days
        last_7days_ticket_ids = ticket_ids.search(domain + [('date_closed', '<=', (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))])
        result['closed_last_7days'] = len(last_7days_ticket_ids)
        if len(ticket_ids) > 0:
            result['closed_success_last_7days'] = len(ticket_ids.filtered(lambda x:x.is_sla_success)) / len(ticket_ids)
            result['closed_rating_last_7days'] = sum(ticket_ids.mapped('rating_score')) / len(ticket_ids)
        else:
            result['closed_success_last_7days'] = 0
            result['closed_rating_last_7days'] = 0
        
        user_target_id = self.env['res.users'].search([('user_id','=',self.env.user.id)],limit=1)
        result['target_ticket_closed'] = user_target_id.target_ticket_closed
        result['target_ticket_rating'] = user_target_id.target_ticket_rating
        result['target_ticket_success'] = user_target_id.target_ticket_success

        ticket_analysis = self.env['report.project.ticket.analysis'].search([('user_id','=',self.env.user.id)])
        return result