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
        'avatar.mixin',
    ]
    _rec_names_search = ['name', 'email', 'ref', 'contact_name']
    
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        year_id = self._context.get('default_elect_year_id')
        if year_id:
            search_domain = ['|', ('id', 'in', stages.ids), '|', ('elect_year_id', '=', False), ('elect_year_id', '=', year_id)]
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

    tag_ids = fields.Many2many(
        'vote.elect.member.tag', 'vote_elect_member_tag_rel', 'member_id', 'tag_id', string='Tags',
        help="Classify and analyze your lead/opportunity categories like: Training, Service")
    color = fields.Integer('Color Index', default=0)
    
    # Customer / contact
    partner_id = fields.Many2one(
        'res.partner', string='Customer', check_company=True, index=True, tracking=10,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")

    contact_name = fields.Char('Candidate Name', tracking=30,compute='_compute_contact_name', copy=False, readonly=False, store=True)
    partner_name = fields.Char(
        'Company Name', tracking=20, index=True,
        compute='_compute_partner_name', readonly=False, store=True,copy=False,
        help='The name of the future partner company that will be created while converting the lead into opportunity')
    title = fields.Many2one('res.partner.title', string='Title', compute='_compute_title', readonly=False, store=True)
    email_from = fields.Char(
        'Email', tracking=40, index=True,copy=False,
        compute='_compute_email_from', inverse='_inverse_email_from', readonly=False, store=True)
    phone = fields.Char(
        'Phone', tracking=50,
        compute='_compute_phone', inverse='_inverse_phone', copy=False,readonly=False, store=True)
    mobile = fields.Char('Mobile', compute='_compute_mobile', copy=False, readonly=False, store=True)
    phone_state = fields.Selection([
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect')], string='Phone Quality', compute="_compute_phone_state", store=True)
    email_state = fields.Selection([
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect')], string='Email Quality', compute="_compute_email_state", store=True)
    website = fields.Char('Website', index=True, help="Website of the contact", compute="_compute_website", readonly=False, store=True)

    # Address fields
    street = fields.Char('Street', compute='_compute_partner_address_values', readonly=False, store=True)
    street2 = fields.Char('Street2', compute='_compute_partner_address_values', readonly=False, store=True)
    zip = fields.Char('Zip', change_default=True, compute='_compute_partner_address_values', readonly=False, store=True)
    city = fields.Char('City', compute='_compute_partner_address_values', readonly=False, store=True)
    state_id = fields.Many2one(
        "res.country.state", string='State',
        compute='_compute_partner_address_values', readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country',
        compute='_compute_partner_address_values', readonly=False, store=True)
    user_id = fields.Many2one(
        'res.users', string='Officer', default=lambda self: self.env.user,
        domain="['&', ('share', '=', False), ('company_ids', 'in', user_company_ids)]",
        check_company=True, index=True, tracking=True)
    user_company_ids = fields.Many2many(
        'res.company', compute='_compute_user_company_ids',
        help='UX: Limit to lead company or all if no company')
    
    # UX
    partner_email_update = fields.Boolean('Partner Email will Update', compute='_compute_partner_email_update')
    partner_phone_update = fields.Boolean('Partner Phone will Update', ) #compute='_compute_partner_phone_update')


    # Constituency fields
    const_type_id = fields.Many2one('vote.const.type', string='Constituency Type', required=True)
    const_id = fields.Many2one('vote.const', string='Constituency', 
                                    domain="[('const_type_id','=',const_type_id)]",
                                    required=True
                                   )
    const_code = fields.Char(related='const_id.code')
    
    pol_partner_id = fields.Many2one('res.partner', string='Political Party', 
                                     domain="[('is_pol_party','=',True)]",
                                     required=True
                                    )

    vote_sign_id = fields.Many2one('vote.sign', string='Sign', store=True, readonly=False, compute="_compute_sign")
    #vote_sign_image = fields.Binary('vote_sign_id.image_1920', readonly=True)
    vote_sn = fields.Char('Vote Serial')
    
    member_ref_line = fields.One2many('vote.elect.member.ref', 'elect_member_id', 'Reference')
    

    # ----------------------------------------------------
    # ------------------- CRUD ---------------------
    # ----------------------------------------------------
    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('vote.elect.member') or _('New')

        result = super(VoteElectMember, self).create(vals)
        return result

    
    @api.depends('pol_partner_id')
    def _compute_sign(self):
        for record in self:
            record.vote_sign_id = record.pol_partner_id.vote_sign_id.id
        
    @api.depends('elect_year_id')
    def _compute_stage_id(self):
        for mem in self:
            if not mem.stage_id:
                mem.stage_id = mem._stage_find(domain=[('fold', '=', False)]).id
    
    def _stage_find(self, elect_year_id=False, domain=None, order='sequence, id', limit=1):
        
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
        return self.env['vote.elect.stage'].search(search_domain, order=order, limit=limit)

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

class MemberRef(models.Model):
    _name = 'vote.elect.member.ref'
    _description = 'Member References'
    
    elect_member_id = fields.Many2one('vote.elect.member', string='Member', required=True, ondelete='cascade', index=True, copy=False)
    member_ref_type_id = fields.Many2one('vote.member.ref.type', string='Ref Type', required=True)
    name = fields.Char('Name', required=True)

    
    