# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class Lead(models.Model):
    _inherit = "crm.lead"

    is_kyb = fields.Boolean(default=False, compute='_compute_kyb', store=True)
    xpl_id = fields.Char('Xpendless ID', readonly=True)
    
    stage_id = fields.Many2one(
        'crm.stage', string='Stage', index=True, tracking=True,
        compute='_compute_stage_id', 
        readonly=False, store=True,
        copy=False, 
        group_expand='_read_group_stage_ids', 
        ondelete='restrict',
        domain="[('id', 'in', stage_ids)]"
    )
    stage_ids = fields.Many2many('crm.stage', compute='_compute_conditional_tage_ids')
    allow_verify = fields.Boolean(related='stage_id.allow_verify')

    reg_no = fields.Char(related='partner_id.reg_no', readonly=False)
    
    usage_est_users = fields.Selection([
        ('1', 'Just Me'), 
        ('2-20', '2 - 20 Employees'),
        ('21-100', '21 - 100 Employees'),
        ('100+', '100+ Employees')
    ],string="Expected Users")
    usage_est_spending = fields.Selection([
        ('0-50000', '0.00 QAR - 50,000.00 QAR'), 
        ('50000-100000', '50,000.00 QAR - 100,000.00 QAR'), 
        ('100000-500000', '100,000.00 QAR - 500,000.00 QAR'), 
        ('500000+', 'Over 500,000.00 QAR')
    ],string="Expected Spending")
    usage_card = fields.Selection([
        ('qatar', 'Qatar Only'), 
        ('international', 'International'),
        ('both', 'Both'),
    ],string="Card Usage")
    work_type = fields.Char('Nature of Work')

    crc = fields.Binary(string="Commercial Registration Certificate", )
    crc_filename = fields.Char(string="CRC Filename")
    
    aoa = fields.Binary(string="Articles of Association", )
    aoa_filename = fields.Char(string="AoA Filename")
    
    c_card = fields.Binary(string="Computer Card", )
    cc_filename = fields.Char(string="CC Filename")
    
    iban_cert = fields.Binary(string="IBAN Certificate", )
    iban_cert_filename = fields.Char(string="IBAN Filename")
    
    trade_license = fields.Binary(string="Trade License")
    trade_license_filename = fields.Char(string="TL Filename")

    @api.depends('team_id','stage_id')
    def _compute_kyb(self):
        for lead in self:
            lead.is_kyb = lead.team_id.is_kyb
            
    @api.depends('team_id', 'type','stage_ids','is_kyb')
    def _compute_stage_id(self):
        for lead in self:
            if not lead.stage_id:
                if lead.team_id.is_kyb or lead.is_kyb:
                    domain = [('is_kyb', '=', True)] if lead.team_id else [('fold', '=', False)]
                else:
                    domain = [('is_kyb', '!=', True)] if lead.team_id else [('fold', '=', False)]
                lead.stage_id = lead._stage_find(domain=domain).id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        # retrieve team_id from the context and write the domain
        # - ('id', 'in', stages.ids): add columns that should be present
        # - OR ('fold', '=', False): add default columns that are not folded
        # - OR ('team_ids', '=', team_id), ('fold', '=', False) if team_id: add team columns that are not folded
        team_id = self._context.get('default_team_id')
        team = self.env['crm.team'].browse(team_id)
        search_domain = []
        if team:
            if team.is_kyb:
                search_domain = [('is_kyb', '=', True)]
            else:
                search_domain = [('is_kyb', '!=', True)]
                #search_domain = ['|', ('id', 'in', stages.ids), '|', ('team_id', '=', False), ('team_id', '=', team_id),('is_kyb', '!=', True)]
        #else:
        #    search_domain = ['|', ('id', 'in', stages.ids), ('team_id', '=', 100)]

        # perform search
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)
        
    @api.depends('team_id')
    def _compute_conditional_tage_ids(self):
        stage_ids = self.env['crm.stage']
        for record in self:
            if record.team_id.is_kyb:
                stage_ids = self.env['crm.stage'].search([('is_kyb','=',True)])
            else:
                stage_ids = self.env['crm.stage'].search([('is_kyb','!=',True)])
            record.stage_ids = stage_ids

    def action_verification(self):
        pass

    # Actions
    def _cron_import_company_from_xpl(self):
        raise UserError('hello')
