# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ProjectTaskSLALine(models.Model):
    _name = 'project.task.sla.line'
    _description = "Task SLA Line"
    _order = 'date_deadline ASC'
    _rec_name = 'prj_sla_id'

    task_id = fields.Many2one('project.task', string='Ticket', required=True, ondelete='cascade', index=True)
    project_id = fields.Many2one('project.project', store=True, compute='_compute_project_from_task')
    prj_sla_id = fields.Many2one('project.sla', string='SLA', required=True, ondelete='cascade')
    date_deadline = fields.Datetime("Deadline", 
                                    #compute='_compute_deadline', compute_sudo=True, 
                                    store=True)
    date_reached = fields.Datetime('Date Reached', 
                                   help='The date on which the SLA reached')
    
    sla_time = fields.Float(related='prj_sla_id.time')
    sla_stage_id = fields.Many2one(related='prj_sla_id.stage_id')
    
    status = fields.Selection([
        ('failed', 'Failed'), 
        ('reached', 'Reached'), 
        ('ongoing', 'Ongoing')
    ], string="Status",  
        default='ongoing',
    #    compute='_compute_status', compute_sudo=True, search='_search_status'
    )
    
    exceeded_hours = fields.Float("Exceeded Working Hours", compute='_compute_exceeded_hours', compute_sudo=True, store=True, help="Working hours exceeded for reached SLAs compared with deadline. Positive number means the SLA was reached after the deadline.")

    @api.depends('task_id')
    def _compute_project_from_task(self):
        for record in self:
            record.project_id = record.task_id.project_id.id
            

    @api.model
    def _update_sla_status(self, target_stage_id):
        for sla_line in self:
            if sla_line.prj_sla_id.stage_id.id == target_stage_id:
                if sla_line.date_deadline and fields.Datetime.now() > sla_line.date_deadline:
                    sla_line.status = 'failed'
                elif sla_line.date_reached or fields.Datetime.now() <= sla_line.date_deadline:
                    sla_line.status = 'reached'
                else:
                    sla_line.status = 'ongoing'

        
    def _compute_deadline(self):
        pass

    #@api.depends('deadline', 'reached_datetime')
    def _compute_status(self):
        for status in self:
            if status.reached_datetime and status.deadline:  # if reached_datetime, SLA is finished: either failed or succeeded
                status.status = 'reached' if status.reached_datetime < status.deadline else 'failed'
            else:  # if not finished, deadline should be compared to now()
                status.status = 'ongoing' if not status.deadline or status.deadline > fields.Datetime.now() else 'failed'

    @api.model
    def _search_status(self, operator, value):
        """ Supported operators: '=', 'in' and their negative form. """
        # constants
        datetime_now = fields.Datetime.now()
        positive_domain = {
            'failed': ['|', '&', ('reached_datetime', '=', True), ('deadline', '<=', 'reached_datetime'), '&', ('reached_datetime', '=', False), ('deadline', '<=', fields.Datetime.to_string(datetime_now))],
            'reached': ['&', ('reached_datetime', '=', True), ('reached_datetime', '<', 'deadline')],
            'ongoing': ['|', ('deadline', '=', False), '&', ('reached_datetime', '=', False), ('deadline', '>', fields.Datetime.to_string(datetime_now))]
        }
        # in/not in case: we treat value as a list of selection item
        if not isinstance(value, list):
            value = [value]
        # transform domains
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            # "('status', 'not in', [A, B])" tranformed into "('status', '=', C) OR ('status', '=', D)"
            domains_to_keep = [dom for key, dom in positive_domain if key not in value]
            return expression.OR(domains_to_keep)
        else:
            return expression.OR(positive_domain[value_item] for value_item in value)
