# -*- coding: utf-8 -*-
import json
import random
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError

class AdmissionTeam(models.Model):
    _inherit = "oe.admission.team"

    dashboard_button_name = fields.Char(string="Dashboard Button", compute='_compute_dashboard_button_name')
    dashboard_graph_data = fields.Text(compute='_compute_dashboard_graph')

    def _graph_get_model(self):
        return 'oe.admission'

    def _graph_y_query(self):
        return 'count(*)'
        #return super(AdmissionTeam,self)._graph_y_query()
        
    def _compute_dashboard_button_name(self):
        for record in self:
            record.dashboard_button_name = record.name

    def action_primary_channel_button(self):
        self.ensure_one()
        
        return super(AdmissionTeam,self).action_primary_channel_button()


    def _compute_dashboard_graph(self):
        for team in self:
            team.dashboard_graph_data = json.dumps(team._get_dashboard_graph_data())