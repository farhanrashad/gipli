# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import random

from babel.dates import format_date
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.tools.safe_eval import safe_eval
from odoo.release import version



class ElectionYear(models.Model):
    _name = "vote.elect.year"
    _description = "Election Year"
    _order = "name asc"

    READONLY_STATES = {
        'progress': [('readonly', True)],
        'close': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    
    active = fields.Boolean(default=True)
    name = fields.Char(string='Name', required=True, index='trigram', translate=True)
    date_start = fields.Date(string='Start Date',  compute='_compute_all_dates', store=True, readonly=False, required=True, states=READONLY_STATES,)
    date_end = fields.Date(string='End Date',  compute='_compute_all_dates', store=True, readonly=False, required=True, states=READONLY_STATES,)
    description = fields.Html(string='Description')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'Open'),
        ('close', 'Closed'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    # ------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------

    #TODO JEM : refactor this stuff with xml action, proper customization,
    @api.model
    def action_elect_member(self):
        action = self.env["ir.actions.actions"]._for_xml_id("de_vote.action_elect_member_pipeline")
        return self._action_update_to_pipeline(action)

    @api.model
    def _action_update_to_pipeline(self, action):
        year_id = self.env['vote.elect.year'].search([('state','=','progress')],limit=1).id
        if year_id:
            # To ensure that the team is readable in multi company
            year_id = self.env['vote.elect.year'].search([('state','=','progress')],limit=1).id
        else:
            year_id = self.env['vote.elect.year'].search([('state','=','progress')],limit=1).id
            action['help'] = "<p class='o_view_nocontent_smiling_face'>%s</p><p>" % _("Create an Opportunity")
            if year_id:
                if self.user_has_groups('de_vote.group_vote_manager'):
                    action['help'] += "<p>%s</p>" % _("""As you are a member of no Sales Team, you are showed the Pipeline of the <b>first team by default.</b>
                                        To work with the CRM, you should <a name="%d" type="action" tabindex="-1">join a team.</a>""",
                                        self.env.ref('de_vote.action_elect_year').id)
                else:
                    action['help'] += "<p>%s</p>" % _("""As you are a member of no Sales Team, you are showed the Pipeline of the <b>first team by default.</b>
                                        To work with the CRM, you should join a team.""")
        action_context = safe_eval(action['context'], {'uid': self.env.uid})
        if year_id:
            action_context['default_elect_year_id'] = year_id
        action['context'] = action_context
        return action
    

    def unlink(self):
        for record in self:
            if record.state != 'draft' and record.no_of_applicants > 0:
                raise exceptions.UserError("You cannot delete a record with applicants when the status is not 'Draft'.")
        return super(AdmissionRegister, self).unlink()

    def button_draft(self):
        self.write({'state': 'draft'})
        return {}

    def button_open(self):
        self.write({'state': 'progress'})
        return {}

    def button_close(self):
        self.write({'state': 'close'})
        return {}
        
    def button_cancel(self):
        self.write({'state': 'draft'})
        return {}

    