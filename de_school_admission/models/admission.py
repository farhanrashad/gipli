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


class Admission(models.Model):
    _name = "oe.admission"
    _description = 'Admission'
    _inherit = [
        'mail.thread.cc',
        'mail.thread.blacklist',
        #'mail.thread.phone',
        'mail.activity.mixin',
        'utm.mixin',
        'format.address.mixin',
    ]
    _primary_email = 'email_from'
    _check_company_auto = True


    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    
    # Description
    name = fields.Char(string='Reference', copy=False, readonly=True, index=True, default=lambda self: _('New'))

    user_id = fields.Many2one(
        'res.users', string='Admission Officer', default=lambda self: self.env.user,
        domain="['&', ('share', '=', False), ('company_ids', 'in', user_company_ids)]",
        check_company=True, index=True, tracking=True)
    user_company_ids = fields.Many2many(
        'res.company', compute='_compute_user_company_ids',
        help='UX: Limit to lead company or all if no company')
    user_email = fields.Char('User Email', related='user_id.email', readonly=True)
    user_login = fields.Char('User Login', related='user_id.login', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, compute='_compute_company_id', readonly=False, store=True)
    team_id = fields.Many2one(
        'oe.admission.team', string='Admission Team', check_company=True, index=True, tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        compute='_compute_team_id', ondelete="set null", readonly=False, store=True)

    referred = fields.Char('Referred By')
    description = fields.Html('Notes')
    active = fields.Boolean('Active', default=True, tracking=True)
    type = fields.Selection([
        ('lead', 'Lead'), ('opportunity', 'Opportunity')],
        index=True, required=True, tracking=15,
        default=lambda self: 'lead' if self.env['res.users'].has_group('de_school_team.group_school_admission_user') else 'opportunity')
    
    # Pipeline management
    stage_id = fields.Many2one(
        'oe.admission.stage', string='Stage', index=True, tracking=True,
        compute='_compute_stage_id', readonly=False, store=True,
        copy=False, group_expand='_read_group_stage_ids', ondelete='restrict',
        domain="['|', ('team_id', '=', False), ('team_id', '=', team_id)]")
    kanban_state = fields.Selection([
        ('grey', 'No next activity planned'),
        ('red', 'Next activity late'),
        ('green', 'Next activity is planned')], string='Kanban State',
        compute='_compute_kanban_state')
    tag_ids = fields.Many2many(
        'oe.admission.tag', 'admission_admission_tag_rel', 'lead_id', 'tag_id', string='Tags',
        help="Classify and analyze your lead/opportunity categories like: Training, Service")
    color = fields.Integer('Color Index', default=0)
    
    # Customer / contact
    partner_id = fields.Many2one(
        'res.partner', string='Customer', check_company=True, index=True, tracking=10,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")
    partner_is_blacklisted = fields.Boolean('Partner is blacklisted', related='partner_id.is_blacklisted', readonly=True)
    contact_name = fields.Char('Contact Name', tracking=30,compute='_compute_contact_name', readonly=False, store=True)
    partner_name = fields.Char(
        'Company Name', tracking=20, index=True,
        compute='_compute_partner_name', readonly=False, store=True,
        help='The name of the future partner company that will be created while converting the lead into opportunity')
    title = fields.Many2one('res.partner.title', string='Title', compute='_compute_title', readonly=False, store=True)
    email_from = fields.Char(
        'Email', tracking=40, index=True,
        compute='_compute_email_from', inverse='_inverse_email_from', readonly=False, store=True)
    phone = fields.Char(
        'Phone', tracking=50,
        compute='_compute_phone', inverse='_inverse_phone', readonly=False, store=True)
    mobile = fields.Char('Mobile', compute='_compute_mobile', readonly=False, store=True)
    phone_state = fields.Selection([
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect')], string='Phone Quality', compute="_compute_phone_state", store=True)
    email_state = fields.Selection([
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect')], string='Email Quality', compute="_compute_email_state", store=True)
    website = fields.Char('Website', index=True, help="Website of the contact", compute="_compute_website", readonly=False, store=True)
    lang_id = fields.Many2one(
        'res.lang', string='Language',
        compute='_compute_lang_id', readonly=False, store=True)
    
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
    
    company_currency = fields.Many2one("res.currency", string='Currency', compute="_compute_company_currency", readonly=True)

    # UX
    partner_email_update = fields.Boolean('Partner Email will Update', compute='_compute_partner_email_update')
    partner_phone_update = fields.Boolean('Partner Phone will Update', ) #compute='_compute_partner_phone_update')
    
    #priority = fields.Selection(string='Priority', index=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], string='Priority',)

    date_conversion = fields.Datetime('Conversion Date', readonly=True)
    date_deadline = fields.Date('Expected Closing', help="Estimate of the date on which the opportunity will be won.")
    date_closed = fields.Datetime('Closed Date', readonly=True, copy=False)

    
    # Accept and Reject
    won_status = fields.Selection([
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('pending', 'Pending'),
    ], string='Is Won', compute='_compute_won_status', store=True)
    lost_reason_id = fields.Many2one(
        'oe.admission.lost.reason', string='Lost Reason',
        index=True, ondelete='restrict', tracking=True)

    # Academic Fields
    admission_register_id = fields.Many2one('oe.admission.register',string="Admission Register", required=True)
    
    course_id = fields.Many2one('oe.school.course', string='Course', compute='_compute_from_admission_register')
    course_code = fields.Char(related='course_id.code')
    batch_id = fields.Many2one('oe.school.course.batch', string='Batch')

    # Probability (Opportunity only)
    is_application_score = fields.Boolean(string='Allow Score', compute='_compute_admission_setting_values')
    is_application_revenue = fields.Boolean(string='Allow Expected Revenue', compute='_compute_admission_setting_values')
    probability = fields.Float(
        'Probability', group_operator="avg", copy=False,
        compute='_compute_probabilities', readonly=False, store=True)
    expected_revenue = fields.Monetary('Expected Revenue', currency_field='company_currency', tracking=True)
    prorated_revenue = fields.Monetary('Prorated Revenue', currency_field='company_currency', store=True, compute="_compute_prorated_revenue")

    
    # ------------------------------------------------------
    # ----------------- Computed Methods -------------------
    # ------------------------------------------------------
    def _compute_admission_setting_values(self):
        application_score = self.env['ir.config_parameter'].sudo().get_param('de_school_admission.is_application_score', False)
        application_revenue = self.env['ir.config_parameter'].sudo().get_param('de_school_admission.is_application_revenue', False)

        for record in self:
            record.is_application_score = application_score
            record.is_application_revenue = application_revenue
    
    @api.depends('active', 'probability','stage_id')
    def _compute_won_status(self):
        for lead in self:
            if lead.active and lead.probability == 100:
                lead.won_status = 'won'
            elif not lead.active and lead.probability == 0:
                lead.won_status = 'lost'
            else:
                if lead.stage_id.is_close:
                    lead.won_status = 'won'
                else:
                    lead.won_status = 'pending'
        
        
    #@api.depends(lambda self: ['stage_id', 'team_id'] + self._pls_get_safe_fields())
    @api.depends('stage_id', 'admission_register_id', 
                 'admission_register_id.score_ids', 'admission_register_id.score_ids.score')
    def _compute_probabilities(self):
        for admission in self:
            if admission.stage_id:
                # Filter the score_ids related to the admission register that are below the current stage
                stage_scores = admission.admission_register_id.score_ids.filtered(
                    lambda line: line.stage_id.sequence <= admission.stage_id.sequence
                )
                
                # Calculate the total score as the sum of stage scores
                total_score = sum(stage_scores.mapped('score'))
                # Calculate the probability based on the total score
                admission.probability = (total_score / 100) * 100
            else:
                admission.probability = 0


                    
    @api.depends('expected_revenue', 'probability')
    def _compute_prorated_revenue(self):
        for lead in self:
            lead.prorated_revenue = round((lead.expected_revenue or 0.0) * (lead.probability or 0) / 100.0, 2)

    def _pls_get_safe_fields(self):
        """ As config_parameters does not accept M2M field,
            we the fields from the formated string stored into the Char config field.
            To avoid sql injections when using that list, we return only the fields
            that are defined on the model. """
        pls_fields_config = self.env['ir.config_parameter'].sudo().get_param('crm.pls_fields')
        pls_fields = pls_fields_config.split(',') if pls_fields_config else []
        pls_safe_fields = [field for field in pls_fields if field in self._fields.keys()]
        return pls_safe_fields

    
    
    @api.depends('admission_register_id')
    def _compute_from_admission_register(self):
        for record in self:
            record.course_id = record.admission_register_id.course_id.id

    @api.depends('company_id')
    def _compute_user_company_ids(self):
        all_companies = self.env['res.company'].search([])
        for admission in self:
            if not admission.company_id:
                admission.user_company_ids = all_companies
            else:
                admission.user_company_ids = admission.company_id
                
    @api.depends('team_id', 'type')
    def _compute_stage_id(self):
        for lead in self:
            if not lead.stage_id:
                lead.stage_id = lead._stage_find(domain=[('fold', '=', False)]).id
    
    def _stage_find(self, team_id=False, domain=None, order='sequence, id', limit=1):
        """ Determine the stage of the current lead with its teams, the given domain and the given team_id
            :param team_id
            :param domain : base search domain for stage
            :param order : base search order for stage
            :param limit : base search limit for stage
            :returns oe.admission.stage recordset
        """
        # collect all team_ids by adding given one, and the ones related to the current leads
        team_ids = set()
        if team_id:
            team_ids.add(team_id)
        for lead in self:
            if lead.team_id:
                team_ids.add(lead.team_id.id)
        # generate the domain
        if team_ids:
            search_domain = ['|', ('team_id', '=', False), ('team_id', 'in', list(team_ids))]
        else:
            search_domain = [('team_id', '=', False)]
        # AND with the domain in parameter
        if domain:
            search_domain += list(domain)
        # perform search, return the first found
        return self.env['oe.admission.stage'].search(search_domain, order=order, limit=limit)

    @api.depends('user_id', 'type')
    def _compute_team_id(self):
        """ When changing the user, also set a team_id or restrict team id
        to the ones user_id is member of. """
        for admission in self:
            # setting user as void should not trigger a new team computation
            if not admission.user_id:
                continue
            user = admission.user_id
            if admission.team_id and user in (admission.team_id.member_ids | admission.team_id.user_id):
                continue
            team_domain = [] #[('use_leads', '=', True)] if lead.type == 'lead' else [('use_leads', '=', True)]
            team = self.env['oe.admission.team']._get_default_team_id(user_id=user.id, domain=team_domain)
            admission.team_id = team.id
    
    @api.depends('user_id', 'team_id', 'partner_id')
    def _compute_company_id(self):
        """ Compute company_id coherency. """
        for lead in self:
            proposal = lead.company_id

            # invalidate wrong configuration
            if proposal:
                # company not in responsible companies
                if lead.user_id and proposal not in lead.user_id.company_ids:
                    proposal = False
                # inconsistent
                if lead.team_id.company_id and proposal != lead.team_id.company_id:
                    proposal = False
                # void company on team and no assignee
                if lead.team_id and not lead.team_id.company_id and not lead.user_id:
                    proposal = False
                # no user and no team -> void company and let assignment do its job
                # unless customer has a company
                if not lead.team_id and not lead.user_id and \
                   (not lead.partner_id or lead.partner_id.company_id != proposal):
                    proposal = False

            # propose a new company based on team > user (respecting context) > partner
            if not proposal:
                if lead.team_id.company_id:
                    proposal = lead.team_id.company_id
                elif lead.user_id:
                    if self.env.company in lead.user_id.company_ids:
                        proposal = self.env.company
                    else:
                        proposal = lead.user_id.company_id & self.env.companies
                elif lead.partner_id:
                    proposal = lead.partner_id.company_id
                else:
                    proposal = False

            # set a new company
            if lead.company_id != proposal:
                lead.company_id = proposal
    
    @api.depends('activity_date_deadline')
    def _compute_kanban_state(self):
        today = date.today()
        for lead in self:
            kanban_state = 'grey'
            if lead.activity_date_deadline:
                lead_date = fields.Date.from_string(lead.activity_date_deadline)
                if lead_date >= today:
                    kanban_state = 'green'
                else:
                    kanban_state = 'red'
            lead.kanban_state = kanban_state
    
    @api.depends('partner_id')
    def _compute_contact_name(self):
        """ compute the new values when partner_id has changed """
        for lead in self:
            lead.update(lead._prepare_contact_name_from_partner(lead.partner_id))
            
    @api.depends('partner_id')
    def _compute_partner_name(self):
        """ compute the new values when partner_id has changed """
        for lead in self:
            lead.update(lead._prepare_partner_name_from_partner(lead.partner_id))
    
    @api.depends('partner_id')
    def _compute_title(self):
        """ compute the new values when partner_id has changed """
        for lead in self:
            if not lead.title or lead.partner_id.title:
                lead.title = lead.partner_id.title
    
    @api.depends('partner_id.email')
    def _compute_email_from(self):
        for lead in self:
            if lead.partner_id.email and lead._get_partner_email_update():
                lead.email_from = lead.partner_id.email

    def _inverse_email_from(self):
        for lead in self:
            if lead._get_partner_email_update():
                lead.partner_id.email = lead.email_from

    @api.depends('partner_id.phone')
    def _compute_phone(self):
        for lead in self:
            if lead.partner_id.phone and lead._get_partner_phone_update():
                lead.phone = lead.partner_id.phone

    def _inverse_phone(self):
        for lead in self:
            if lead._get_partner_phone_update():
                lead.partner_id.phone = lead.phone

    @api.depends('phone', 'country_id.code')
    def _compute_phone_state(self):
        for lead in self:
            phone_status = False
            if lead.phone:
                country_code = lead.country_id.code if lead.country_id and lead.country_id.code else None
                try:
                    if phone_validation.phone_parse(lead.phone, country_code):  # otherwise library not installed
                        phone_status = 'correct'
                except UserError:
                    phone_status = 'incorrect'
            lead.phone_state = phone_status

    @api.depends('email_from')
    def _compute_email_state(self):
        for lead in self:
            email_state = False
            if lead.email_from:
                email_state = 'incorrect'
                for email in email_split(lead.email_from):
                    if mail_validation.mail_validate(email):
                        email_state = 'correct'
                        break
            lead.email_state = email_state

    def _get_partner_email_update(self):
        """Calculate if we should write the email on the related partner. When
        the email of the lead / partner is an empty string, we force it to False
        to not propagate a False on an empty string.

        Done in a separate method so it can be used in both ribbon and inverse
        and compute of email update methods.
        """
        self.ensure_one()
        if self.partner_id and self.email_from != self.partner_id.email:
            lead_email_normalized = tools.email_normalize(self.email_from) or self.email_from or False
            partner_email_normalized = tools.email_normalize(self.partner_id.email) or self.partner_id.email or False
            return lead_email_normalized != partner_email_normalized
        return False

    def _get_partner_phone_update(self):
        """Calculate if we should write the phone on the related partner. When
        the phone of the lead / partner is an empty string, we force it to False
        to not propagate a False on an empty string.

        Done in a separate method so it can be used in both ribbon and inverse
        and compute of phone update methods.
        """
        self.ensure_one()
        if self.partner_id and self.phone != self.partner_id.phone:
            lead_phone_formatted = self.phone_get_sanitized_number(number_fname='phone') or self.phone or False
            partner_phone_formatted = self.partner_id.phone_get_sanitized_number(number_fname='phone') or self.partner_id.phone or False
            return lead_phone_formatted != partner_phone_formatted
        return False

    @api.depends('email_from', 'partner_id')
    def _compute_partner_email_update(self):
        for lead in self:
            lead.partner_email_update = lead._get_partner_email_update()
            
    @api.depends('phone', 'partner_id')
    def _compute_partner_phone_update(self):
        for lead in self:
            lead.partner_phone_update = lead._get_partner_phone_update()
            
    def _prepare_partner_name_from_partner(self, partner):
        """ Company name: name of partner parent (if set) or name of partner
        (if company) or company_name of partner (if not a company). """
        partner_name = partner.parent_id.name
        if not partner_name and partner.is_company:
            partner_name = partner.name
        elif not partner_name and partner.company_name:
            partner_name = partner.company_name
        return {'partner_name': partner_name or self.partner_name} 
    
    def _prepare_contact_name_from_partner(self, partner):
        contact_name = False if partner.is_company else partner.name
        return {'contact_name': contact_name or self.contact_name}
    
    @api.depends('company_id')
    def _compute_company_currency(self):
        for lead in self:
            if not lead.company_id:
                lead.company_currency = self.env.company.currency_id
            else:
                lead.company_currency = lead.company_id.currency_id
    # ----------------------------------------------------
    # ------------------- CRUD ---------------------
    # ----------------------------------------------------
    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('school.admission') or _('New')

        result = super(Admission, self).create(vals)
        return result

    # -------------------------------------------------------
    # ------------------- Button Actions --------------------
    # -------------------------------------------------------
    def action_accept_application(self):
        self.ensure_one()
        self.action_set_won()

        message = self._get_rainbowman_message()
        if message:
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': message,
                    'img_url': '/web/image/%s/%s/image_1024' % (self.team_id.user_id._name, self.team_id.user_id.id) if self.team_id.user_id.image_1024 else '/web/static/img/smile.svg',
                    'type': 'rainbow_man',
                }
            }
        return True

    def action_set_won(self):
        """ Won semantic: probability = 100 (active untouched) """
        self.action_unarchive()
        # group the leads by team_id, in order to write once by values couple (each write leads to frequency increment)
        leads_by_won_stage = {}
        for lead in self:
            won_stages = self._stage_find(domain=[('is_close', '=', True)], limit=None)
            # ABD : We could have a mixed pipeline, with "won" stages being separated by "standard"
            # stages. In the future, we may want to prevent any "standard" stage to have a higher
            # sequence than any "won" stage. But while this is not the case, searching
            # for the "won" stage while alterning the sequence order (see below) will correctly
            # handle such a case :
            #       stage sequence : [x] [x (won)] [y] [y (won)] [z] [z (won)]
            #       when in stage [y] and marked as "won", should go to the stage [y (won)],
            #       not in [x (won)] nor [z (won)]
            stage_id = next((stage for stage in won_stages if stage.sequence > lead.stage_id.sequence), None)
            if not stage_id:
                stage_id = next((stage for stage in reversed(won_stages) if stage.sequence <= lead.stage_id.sequence), won_stages)
            if stage_id in leads_by_won_stage:
                leads_by_won_stage[stage_id] += lead
            else:
                leads_by_won_stage[stage_id] = lead
        for won_stage_id, leads in leads_by_won_stage.items():
            leads.write({'stage_id': won_stage_id.id, 'probability': 100})
        return True
        
    def get_rainbowman_message(self):
        self.ensure_one()
        if self.stage_id.is_won:
            return self._get_rainbowman_message()
        return False

    def _get_rainbowman_message(self):
        if not self.user_id or not self.team_id:
            return False
        if not self.expected_revenue:
            # Show rainbow man for the first won lead of a salesman, even if expected revenue is not set. It is not
            # very often that leads without revenues are marked won, so simply get count using ORM instead of query
            today = fields.Datetime.today()
            user_won_leads_count = self.search_count([
                ('type', '=', 'opportunity'),
                ('user_id', '=', self.user_id.id),
                ('probability', '=', 100),
                ('date_closed', '>=', date_utils.start_of(today, 'year')),
                ('date_closed', '<', date_utils.end_of(today, 'year')),
            ])
            if user_won_leads_count == 1:
                return _('Go, go, go! Congrats for your first deal.')
            return False

        self.flush_model()  # flush fields to make sure DB is up to date
        query = """
            SELECT
                SUM(CASE WHEN user_id = %(user_id)s THEN 1 ELSE 0 END) as total_won,
                MAX(CASE WHEN date_closed >= CURRENT_DATE - INTERVAL '30 days' AND user_id = %(user_id)s THEN expected_revenue ELSE 0 END) as max_user_30,
                MAX(CASE WHEN date_closed >= CURRENT_DATE - INTERVAL '7 days' AND user_id = %(user_id)s THEN expected_revenue ELSE 0 END) as max_user_7,
                MAX(CASE WHEN date_closed >= CURRENT_DATE - INTERVAL '30 days' AND team_id = %(team_id)s THEN expected_revenue ELSE 0 END) as max_team_30,
                MAX(CASE WHEN date_closed >= CURRENT_DATE - INTERVAL '7 days' AND team_id = %(team_id)s THEN expected_revenue ELSE 0 END) as max_team_7
            FROM oe_admission
            WHERE
                type = 'opportunity'
            AND
                active = True
            AND
                probability = 100
            AND
                DATE_TRUNC('year', date_closed) = DATE_TRUNC('year', CURRENT_DATE)
            AND
                (user_id = %(user_id)s OR team_id = %(team_id)s)
        """
        self.env.cr.execute(query, {'user_id': self.user_id.id,
                                    'team_id': self.team_id.id})
        query_result = self.env.cr.dictfetchone()

        message = False
        if query_result['total_won'] == 1:
            message = _('Go, go, go! Congrats for your first deal.')
        elif query_result['max_team_30'] == self.expected_revenue:
            message = _('Boom! Team record for the past 30 days.')
        elif query_result['max_team_7'] == self.expected_revenue:
            message = _('Yeah! Deal of the last 7 days for the team.')
        elif query_result['max_user_30'] == self.expected_revenue:
            message = _('You just beat your personal record for the past 30 days.')
        elif query_result['max_user_7'] == self.expected_revenue:
            message = _('You just beat your personal record for the past 7 days.')
        return message

    def action_set_lost(self, **additional_values):
        """ Lost semantic: probability = 0 or active = False """
        res = self.action_archive()
        if additional_values:
            self.write(dict(additional_values))
        return res

    def action_application_lost(self):
        self.ensure_one()
        active_id = self.env.context.get('admission_id')
        context = {
            'default_type': 'opportunity',
        }
        if active_id:
            context['default_admission_id'] = active_id
        return {
            'name': 'Lost Reason',
            'view_mode': 'form',
            'res_model': 'oe.admission.lost.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
    def toggle_active(self):
        """ When archiving: mark probability as 0. When re-activating
        update probability again, for leads and opportunities. """
        res = super(Admission, self).toggle_active()
        activated = self.filtered(lambda lead: lead.active)
        archived = self.filtered(lambda lead: not lead.active)
        if activated:
            activated.write({'lost_reason_id': False})
            activated._compute_probabilities()
        if archived:
            archived.write({'probability': 0})
        return res