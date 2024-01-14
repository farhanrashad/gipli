# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pytz
import threading
from collections import OrderedDict, defaultdict
from datetime import date, datetime, timedelta
from psycopg2 import sql

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.addons.iap.tools import iap_tools
from odoo.addons.mail.tools import mail_validation
#from odoo.addons.phone_validation.tools import phone_validation
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools.translate import _
from odoo.tools import date_utils, email_re, email_split, is_html_empty


_logger = logging.getLogger(__name__)


class VoteElectMember(models.Model):
    _name = "vote.elect.member"
    _description = 'Election Member'
    _inherit = [
        #'mail.thread.cc',
        #'mail.thread.blacklist',
        #'mail.thread.phone',
        'mail.activity.mixin',
        'utm.mixin',
        'format.address.mixin',
    ]
    
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        # retrieve team_id from the context and write the domain
        # - ('id', 'in', stages.ids): add columns that should be present
        # - OR ('fold', '=', False): add default columns that are not folded
        # - OR ('team_ids', '=', team_id), ('fold', '=', False) if team_id: add team columns that are not folded
        team_id = self._context.get('default_elect_year_id')
        if team_id:
            search_domain = ['|', ('id', 'in', stages.ids), '|', ('elect_year_id', '=', False), ('elect_year_id', '=', team_id)]
        else:
            search_domain = ['|', ('id', 'in', stages.ids), ('elect_year_id', '=', False)]

        # perform search
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    
    # Description
    name = fields.Char(string='Reference', copy=False, readonly=True, index=True, default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', string='Company', index=True, compute='_compute_company_id', readonly=False, store=True)
    description = fields.Html('Notes')
    active = fields.Boolean('Active', default=True, tracking=True)

    elect_year_id = fields.Many2one(
        'vote.elect.year', string='Election Year', check_company=True, index=True, tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        #compute='_compute_elect_year_id', 
        ondelete="set null", readonly=False, store=True)
    
    # Pipeline management
    stage_id = fields.Many2one(
        'vote.elect.stage', string='Stage', index=True, tracking=True,
        compute='_compute_stage_id', readonly=False, store=True,
        copy=False, group_expand='_read_group_stage_ids', ondelete='restrict',
        domain="['|', ('elect_year_id', '=', False), ('elect_year_id', '=', elect_year_id)]")
    kanban_state = fields.Selection([
        ('grey', 'No next activity planned'),
        ('red', 'Next activity late'),
        ('green', 'Next activity is planned')], string='Kanban State',
        compute='_compute_kanban_state')

    color = fields.Integer('Color Index', default=0)
    
    # Customer / contact
    partner_id = fields.Many2one(
        'res.partner', string='Customer', check_company=True, index=True, tracking=10,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")

    user_id = fields.Many2one(
        'res.users', string='Admission Officer', default=lambda self: self.env.user,
        domain="['&', ('share', '=', False), ('company_ids', 'in', user_company_ids)]",
        check_company=True, index=True, tracking=True)
    user_company_ids = fields.Many2many(
        'res.company', compute='_compute_user_company_ids',
        help='UX: Limit to lead company or all if no company')
    
    
    @api.depends('elect_year_id')
    def _compute_stage_id(self):
        for mem in self:
            if not mem.stage_id:
                mem.stage_id = mem._stage_find(domain=[('fold', '=', False)]).id
    
    def _stage_find(self, team_id=False, domain=None, order='sequence, id', limit=1):
        
        elect_year_ids = set()
        if elect_year_id:
            elect_year_ids.add(elect_year_id)
        for mem in self:
            if mem.elect_year_id:
                elect_year_ids.add(mem.elect_year_id.id)
        # generate the domain
        if elect_year_ids:
            search_domain = ['|', ('elect_year_id', '=', False), ('elect_year_id', 'in', list(elect_year_ids))]
        else:
            search_domain = [('elect_year_id', '=', False)]
        # AND with the domain in parameter
        if domain:
            search_domain += list(domain)
        # perform search, return the first found
        return self.env['oe.admission.stage'].search(search_domain, order=order, limit=limit)

    @api.depends('activity_date_deadline')
    def _compute_kanban_state(self):
        today = date.today()
        for mem in self:
            kanban_state = 'grey'
            if mem.activity_date_deadline:
                mem_date = fields.Date.from_string(mem.activity_date_deadline)
                if mem_date >= today:
                    kanban_state = 'green'
                else:
                    kanban_state = 'red'
            mem.kanban_state = kanban_state


    
    