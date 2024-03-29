# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectTaskSLALine(models.Model):
    _name = 'project.task.sla.line'
    _description = "Task SLA Line"
    _order = 'date_deadline ASC'
    _rec_name = 'prj_sla_id'

    task_id = fields.Many2one('project.task', string='Ticket', required=True, ondelete='cascade', index=True)
    prj_sla_id = fields.Many2one('project.sla', string='SLA', required=True, ondelete='cascade')
    date_deadline = fields.Datetime("Deadline", 
                                    #compute='_compute_deadline', compute_sudo=True, 
                                    store=True)
    
    status = fields.Selection([
        ('failed', 'Failed'), 
        ('reached', 'Reached'), 
        ('ongoing', 'Ongoing')
    ], string="Status", 
        compute='_compute_status', compute_sudo=True, search='_search_status')
    
    exceeded_hours = fields.Float("Exceeded Working Hours", compute='_compute_exceeded_hours', compute_sudo=True, store=True, help="Working hours exceeded for reached SLAs compared with deadline. Positive number means the SLA was reached after the deadline.")

    def _compute_deadline(self):
        pass
        
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
