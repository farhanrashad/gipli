# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from odoo.addons.de_helpdesk.models.project_task import TICKET_PRIORITY


class HelpdeskSLAReport(models.Model):
    _name = 'report.project.ticket.sla.analysis'
    _description = "SLA Analysis Report"
    _auto = False
    _order = 'create_date DESC'

    ticket_id = fields.Many2one('project.task', string='Ticket', readonly=True)
    description = fields.Text(readonly=True)
    tag_ids = fields.Many2many('project.tag', relation='project_tag_project_ticket_rel',
        column1='project_ticket_id', column2='project_tag_id',
        string='Tags', readonly=True)
    ticket_ref = fields.Char(string='Ticket IDs Sequence', readonly=True)
    name = fields.Char(string='Subject', readonly=True)
    create_date = fields.Datetime("Ticket Create Date", readonly=True)
    priority = fields.Selection(TICKET_PRIORITY, string='Minimum Priority', readonly=True)
    users_id = fields.Many2one('res.users', string="Assigned To", readonly=True)
    partner_id = fields.Many2one('res.partner', string="Customer", readonly=True)
    partner_name = fields.Char(string='Customer Name', readonly=True)
    partner_email = fields.Char(string='Customer Email', readonly=True)
    partner_phone = fields.Char(string='Customer Phone', readonly=True)
    ticket_type_id = fields.Many2one('project.ticket.type', string="Type", readonly=True)
    stage_id = fields.Many2one('project.task.type', string="Stage", readonly=True)
    #ticket_closed = fields.Boolean("Ticket Closed", readonly=True)
    #ticket_close_hours = fields.Integer("Working Hours to Close", group_operator="avg", readonly=True)
    #ticket_assignation_hours = fields.Integer("Working Hours to Assign", group_operator="avg", readonly=True)
    #close_date = fields.Datetime("Close date", readonly=True)
    sla_id = fields.Many2one('project.sla', string='SLA', readonly=True)
    #sla_ids = fields.Many2many('helpdesk.sla', 'helpdesk_sla_status', 'ticket_id', 'sla_id', string="SLAs", copy=False)
    sla_status_ids = fields.One2many('project.ticket.sla.line', 'ticket_id', string="SLA Status")
    #sla_stage_id = fields.Many2one('helpdesk.stage', string="SLA Stage", readonly=True)
    sla_deadline = fields.Datetime("SLA Deadline", group_operator='min', readonly=True)
    sla_status = fields.Selection([('failed', 'SLA Failed'), ('reached', 'SLA Success'), ('ongoing', 'SLA in Progress')], string="Status", readonly=True)
    sla_fail = fields.Boolean("SLA Status Failed", group_operator='bool_or', readonly=True)
    sla_success = fields.Boolean("SLA Status Success", group_operator='bool_or', readonly=True)
    #sla_exceeded_hours = fields.Integer("Working Hours to Reach SLA", group_operator='avg', readonly=True, help="Day to reach the stage of the SLA, without taking the working calendar into account")
    sla_status_failed = fields.Integer("Number of SLA Failed", readonly=True)
    active = fields.Boolean("Active", readonly=True)
    #rating_last_value = fields.Float("Rating (/5)", group_operator="avg", readonly=True)
    #rating_avg = fields.Float('Average Rating', readonly=True, group_operator='avg')
    team_id = fields.Many2one('project.project', string='Helpdesk Team', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    message_is_follower = fields.Boolean(related='ticket_id.message_is_follower')
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State', readonly=True)

    def _select(self):
        return """
            SELECT DISTINCT 
                t.id as id,
                t.id as ticket_id,
                t.description,
                t.ticket_no as ticket_ref,
                t.name as name,
                t.create_date as create_date, 
                t.project_id as team_id,
                t.active as active,
                t.stage_id as stage_id,
                t.prj_ticket_type_id as ticket_type_id, 
                t.partner_id,
                c.name as partner_name,
                t.partner_email as partner_email,
                t.partner_phone as partner_phone,
                t.company_id,
                t.state as kanban_state,
                t.ticket_priority as priority,
                stage.fold as ticket_closed,
                sla.stage_id as sla_stage_id,
                tsla.date_deadline as sal_deadline,
                sla.id as sla_id,
                tsla.date_reached >= tsla.date_deadline OR (tsla.date_reached IS NULL AND tsla.date_deadline < NOW() AT TIME ZONE 'UTC') AS sla_fail,
                CASE
                    WHEN tsla.date_reached IS NOT NULL AND tsla.date_deadline IS NOT NULL AND tsla.date_reached >= tsla.date_deadline THEN 1
                    WHEN tsla.date_reached IS NULL AND tsla.date_deadline IS NOT NULL AND tsla.date_deadline < NOW() AT TIME ZONE 'UTC' THEN 1
                    ELSE 0
                END AS sla_status_failed,
                CASE
                    WHEN tsla.date_reached IS NOT NULL AND (tsla.date_deadline IS NULL OR tsla.date_reached < tsla.date_deadline) THEN 'reached'
                    WHEN (tsla.date_reached IS NOT NULL AND tsla.date_deadline IS NOT NULL AND tsla.date_reached >= tsla.date_deadline) OR
                    (tsla.date_reached IS NULL AND tsla.date_deadline IS NOT NULL AND tsla.date_deadline < NOW() AT TIME ZONE 'UTC') THEN 'failed'
                    WHEN tsla.date_reached IS NULL AND (tsla.date_deadline IS NULL OR tsla.date_deadline > NOW() AT TIME ZONE 'UTC') THEN 'ongoing'
                END AS sla_status,
                CASE
                    WHEN (tsla.date_deadline IS NOT NULL AND tsla.date_deadline > NOW() AT TIME ZONE 'UTC') THEN TRUE ELSE FALSE
                END AS sla_success
        """

    def _group_by(self):
        return """
                t.id,
                stage.fold,
                sla.stage_id,
                tsla.date_deadline,
                tsla.date_reached,
                sla.id,
                c.name
        """

    def _from(self):
        return f"""
            project_task t
            LEFT JOIN project_task_type STAGE ON t.stage_id = stage.id
            RIGHT JOIN project_ticket_sla_line tsla ON t.id = tsla.ticket_id
            LEFT JOIN project_sla sla ON sla.id = tsla.prj_sla_id
            LEFT JOIN res_partner c on t.partner_id = c.id
        """

    def _where(self):
        return """
            t.active = true
        """

    def _order_by(self):
        return """
            id, sla_stage_id
        """

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM %s
            WHERE %s
            GROUP BY %s
            ORDER BY %s
            )""" % (self._table, self._select(), self._from(),
                    self._where(), self._group_by(), self._order_by()))
