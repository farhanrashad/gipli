# -*- coding: utf-8 -*-
import json
import random
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError

class AdmissionTeam(models.Model):
    _inherit = "oe.admission.team"

    opportunities_count = fields.Integer(
        string='# Opportunities', compute='_compute_opportunities_data')
    opportunities_amount = fields.Monetary(
        string='Opportunities Revenues', compute='_compute_opportunities_data')
    
    count_loan_to_pay = fields.Integer(string='Loan Confirm')
    priority = fields.Integer(string='Priority')
    stage_id = fields.Integer(string='stage')

    dashboard_button_name = fields.Char(string="Dashboard Button", compute='_compute_dashboard_button_name')
    dashboard_graph_data = fields.Text(compute='_compute_dashboard_graph')

    def _graph_get_model(self):
        return 'oe.admission'

    def _graph_y_query(self):
        return 'count(*)'
        #return super(AdmissionTeam,self)._graph_y_query()

    def _compute_dashboard_graph(self):
        for team in self:
            team.dashboard_graph_data = json.dumps(team._get_dashboard_graph_data())


    def _compute_opportunities_data(self):
        opportunity_data = self.env['oe.admission']._read_group([
            ('team_id', 'in', self.ids),
            ('type', '=', 'opportunity'),
        ], ['expected_revenue:sum', 'team_id'], ['team_id'])
        counts = {datum['team_id'][0]: datum['team_id_count'] for datum in opportunity_data}
        amounts = {datum['team_id'][0]: datum['expected_revenue'] for datum in opportunity_data}
        for team in self:
            team.opportunities_count = counts.get(team.id, 0)
            team.opportunities_amount = amounts.get(team.id, 0)
            
    # -----------------------------------------------------------------
    # ----------------------- Action buttons- --------------------------
    # ------------------------------------------------------------------
    def action_open_team_admissions_all(self):
        self.ensure_one()
        context = {
            'default_type': 'opportunity',
            'search_default_assigned_to_me': 1,
        }
        return {
            'name': 'Applications',
            'view_type': 'form',
            'view_mode': 'kanban,tree,form',
            'res_model': 'oe.admission',
            'type': 'ir.actions.act_window',
            'context': context,
            'domain': [('team_id','=',self.id)]
        }
    def action_open_team_admissions_pending(self):
        self.ensure_one()
        context = {
            'default_type': 'opportunity',
            'search_default_assigned_to_me': 1,
        }
        return {
            'name': 'Pending Applications',
            'view_type': 'form',
            'view_mode': 'kanban,tree,form',
            'res_model': 'oe.admission',
            'type': 'ir.actions.act_window',
            'context': context,
            'domain': [('team_id','=',self.id),('is_admission_confirmed','!=',True)]
        }
    def action_open_team_admissions_confirm(self):
        self.ensure_one()
        context = {
            'default_type': 'opportunity',
            'search_default_assigned_to_me': 1,
        }
        return {
            'name': 'Applications Confirmed',
            'view_type': 'form',
            'view_mode': 'kanban,tree,form',
            'res_model': 'oe.admission',
            'type': 'ir.actions.act_window',
            'context': context,
            'domain': [('team_id','=',self.id),('is_admission_confirmed','=',True)]
        }

    def action_open_new_admissions(self):
        self.ensure_one()
        active_id = self.env.context.get('active_id')
        context = {
            'default_type': 'opportunity',
        }
        if active_id:
            context['search_default_team_id'] = [active_id]
            context['default_team_id'] = active_id
        return {
            'name': 'Application',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'oe.admission',
            'type': 'ir.actions.act_window',
            'context': context,
        }

    def admission_activity_report_action_team(self):
        self.ensure_one()
        return {
            'name': 'Admission Activities',
            'view_mode': 'graph,pivot,tree',
            'res_model': 'oe.admission.activity.report',
            'type': 'ir.actions.act_window',
        }
        
    def action_admin_config(self):
        self.ensure_one()
        return {
            'name': self.name,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [[False, "form"]],
            'res_model': 'oe.admission.team',
            'res_id': self.id,
        }

    def action_edit_admissions_team(self):
        return {
           'name': 'Admission Team',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'oe.admission.team',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }