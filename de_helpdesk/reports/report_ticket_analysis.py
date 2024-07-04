# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools
from odoo.addons.de_helpdesk.models.project_task import TICKET_PRIORITY
from odoo.addons.rating.models.rating_data import RATING_LIMIT_MIN


class TicketAnalysis(models.Model):
    _name = 'report.project.ticket.analysis'
    _description = "Ticket Analysis"
    _auto = False
    _order = 'create_date DESC'

    ticket_id = fields.Many2one('project.task', string='Ticket', readonly=True)
    description = fields.Text(readonly=True)
    tag_ids = fields.Many2many('project.tag', relation='helpdesk_tag_helpdesk_ticket_rel',
        column1='helpdesk_ticket_id', column2='helpdesk_tag_id',
        string='Tags', readonly=True)
    ticket_ref = fields.Char(string='Ticket IDs Sequence', readonly=True)
    name = fields.Char(string='Subject', readonly=True)
    sla_fail = fields.Boolean(related="ticket_id.is_sla_fail", readonly=True)
    sla_success = fields.Boolean("SLA Status Success", group_operator='bool_or', readonly=True)
    sla_ids = fields.Many2many('project.ticket.sla.line', 'helpdesk_sla_status', 'ticket_id', 'sla_id', string="SLAs", copy=False)
    sla_status_ids = fields.One2many('project.ticket.sla.line', 'ticket_id', string="SLA Status")
    create_date = fields.Datetime("Created On", readonly=True)
    priority = fields.Selection(TICKET_PRIORITY, string='Minimum Priority', readonly=True)
    user_id = fields.Many2one('res.users', string="Assigned To", readonly=True)
    partner_id = fields.Many2one('res.partner', string="Customer", readonly=True)
    partner_name = fields.Char(string='Customer Name', readonly=True)
    partner_email = fields.Char(string='Customer Email', readonly=True)
    partner_phone = fields.Char(string='Customer Phone', readonly=True)
    ticket_type_id = fields.Many2one('helpdesk.ticket.type', string="Type", readonly=True)
    stage_id = fields.Many2one('project.task.type', string="Stage", readonly=True)
    sla_deadline = fields.Datetime("Ticket Deadline", readonly=True)
    ticket_deadline_hours = fields.Float("Hours to SLA Deadline", group_operator="avg", readonly=True)
    close_ticket_hours = fields.Float("Hours to Close", group_operator="avg", readonly=True)
    open_ticket_hours = fields.Float("Hours Open", group_operator="avg", readonly=True)
    #ticket_assignation_hours = fields.Float("Hours to Assign", group_operator="avg", readonly=True)
    close_date = fields.Datetime("Close date", readonly=True)
    assign_date = fields.Datetime("First assignment date", readonly=True)
    #rating_last_value = fields.Float("Rating (/5)", group_operator="avg", readonly=True)
    active = fields.Boolean("Active", readonly=True)
    team_id = fields.Many2one('project.project', string='Helpdesk Team', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    message_is_follower = fields.Boolean(related='ticket_id.message_is_follower')
    kanban_state = fields.Char('Kanban State')
    #kanban_state = fields.Selection([
    #    ('normal', 'Grey'),
    #    ('done', 'Green'),
    #    ('blocked', 'Red')], string='Kanban State', readonly=True)
    #first_response_hours = fields.Float("Hours to First Response", group_operator="avg", readonly=True)
    #avg_response_hours = fields.Float("Average Hours to Respond", group_operator="avg", readonly=True)
    rating_avg = fields.Float('Average Rating', readonly=True, group_operator='avg')

    def _select(self):
        select_str = """
            SELECT t.id AS id,
                   t.id AS ticket_id,
                   t.description,
                   t.ticket_no AS ticket_ref,
                   t.name AS name,
                   t.create_date AS create_date,
                   t.ticket_priority AS priority,
                   u.user_id AS user_id,
                   t.partner_id AS partner_id,
                   p.name AS partner_name,
                   t.partner_email AS partner_email,
                   t.partner_phone AS partner_phone,
                   t.prj_ticket_type_id AS ticket_type_id,
                   t.stage_id AS stage_id,
                   t.sla_date_deadline AS sla_deadline,
                   NULLIF(t.sla_hours_deadline, 0) AS ticket_deadline_hours,
                   NULLIF(t.hours_close, 0) AS close_ticket_hours,
                   EXTRACT(EPOCH FROM (COALESCE(t.date_closed, NOW() AT TIME ZONE 'UTC') - t.create_date)) / 3600 AS open_ticket_hours,
                   t.date_closed AS close_date,
                   t.date_assign AS assign_date,
                   AVG(t.rating_score) as rating_avg,
                   t.active AS active,
                   t.project_id AS team_id,
                   t.company_id AS company_id,
                   t.kanban_state AS kanban_state,
                   CASE
                       WHEN (t.sla_date_deadline IS NOT NULL AND t.sla_date_deadline > NOW() AT TIME ZONE 'UTC') THEN TRUE ELSE FALSE
                   END AS sla_success
        """
        return select_str

    def _group_by(self):
        return """
                t.id,
                u.user_id,
                p.name
        """

    def _from(self):
        from_str = f"""
            project_task t
            LEFT JOIN project_task_user_rel u ON u.task_id = t.id
            LEFT JOIN res_partner p on t.partner_id = p.id
        """
        return from_str

    def _where(self):
        return """
            t.active = true
            and t.is_ticket = True
        """
        
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM %s
            WHERE %s
            GROUP BY %s
            )""" % (self._table, self._select(), self._from(), self._where(), self._group_by()))
