# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_sla = fields.Boolean(related='project_id.is_sla')
    sla_date_deadline = fields.Datetime("SLA Deadline", compute='_compute_all_sla_deadline', compute_sudo=True, store=True)
    sla_hours_deadline = fields.Float("Hours to SLA Deadline", compute='_compute_all_sla_deadline', compute_sudo=True, store=True)

    # Computed Methods
    #@api.depends('sla_status_ids.deadline', 'sla_status_ids.reached_datetime')
    def _compute_all_sla_deadline(self):
        for record in self:
            record.sla_date_deadline = False
            record.sla_hours_deadline = False