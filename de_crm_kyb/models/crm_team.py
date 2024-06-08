# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
import logging
import random
import threading

from ast import literal_eval
from markupsafe import Markup

from odoo import api, exceptions, fields, models, _
from odoo.osv import expression
from odoo.tools import float_compare, float_round
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class Team(models.Model):
    _inherit = "crm.team"

    # ------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------

    #TODO JEM : refactor this stuff with xml action, proper customization,
    @api.model
    def action_my_kyb_pipeline(self):
        action = self.env["ir.actions.actions"]._for_xml_id("crm.crm_lead_action_pipeline")
        return self._action_update_to_kyb_pipeline(action)

    @api.model
    def _action_update_to_kyb_pipeline(self, action):
        user_team_id = self.env.user.sale_team_id.id
        if user_team_id:
            # To ensure that the team is readable in multi company
            user_team_id = self.search([('id', '=', user_team_id)], limit=1).id
        else:
            user_team_id = self.search([], limit=1).id
            action['help'] = "<p class='o_view_nocontent_smiling_face'>%s</p><p>" % _("Create an KYB")
            if user_team_id:
                if self.user_has_groups('sales_team.group_sale_manager'):
                    action['help'] += "<p>%s</p>" % _("""As you are a member of no Sales Team, you are showed the Pipeline of the <b>first team by default.</b>
                                        To work with the CRM, you should <a name="%d" type="action" tabindex="-1">join a team.</a>""",
                                        self.env.ref('sales_team.crm_team_action_config').id)
                else:
                    action['help'] += "<p>%s</p>" % _("""As you are a member of no Sales Team, you are showed the Pipeline of the <b>first team by default.</b>
                                        To work with the CRM, you should join a team.""")
        action_context = safe_eval(action['context'], {'uid': self.env.uid})
        if user_team_id:
            action_context['default_team_id'] = user_team_id

        action['domain'] = [('type','=','opportunity'),('is_kyb', '=', True)]


        # Retrieve the view IDs
        """
        tree_view_id = self.env.ref('crm.crm_lead_action_pipeline_view_tree').id
        kanban_view_id = self.env.ref('crm.crm_lead_action_pipeline_view_kanban').id
        calendar_view_id = self.env.ref('crm.crm_lead_action_pipeline_view_calendar').id
        pivot_view_id = self.env.ref('crm.crm_lead_action_pipeline_view_pivot').id
        graph_view_id = self.env.ref('crm.crm_lead_action_pipeline_view_graph').id
        form_view_id = self.env.ref('de_crm_kyb.crm_lead_kyb_form_view').id

        action['views'] = [
            (kanban_view_id, 'kanban'),
            (tree_view_id, 'tree'),
            (form_view_id, 'form'),
            (calendar_view_id, 'calendar'),
            (pivot_view_id, 'pivot'),
            (graph_view_id, 'graph'),
            (False, 'activity')  # Activity view is a special case and doesn't need an ID
        ]
        """

        # Set the view mode
        action['view_mode'] = 'kanban,tree,form,calendar,pivot,graph,activity'
        
        action['context'] = action_context
        return action